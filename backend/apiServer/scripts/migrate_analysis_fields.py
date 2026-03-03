#!/usr/bin/env python3
"""
Migration script to extract and promote fields from existing analyses:
- Extract "analysis_description" from llmResponse -> top-level "description"
- Extract "execution.parameters" from llmResponse -> top-level "parameters"
"""

import asyncio
import logging
from pathlib import Path
import sys
from typing import Dict, Any, Optional

# Add project paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "shared"))

from shared.db.mongodb_client import MongoDBClient
from shared.config.database import DatabaseConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisFieldMigrator:
    """Migrates analysis fields from nested to top-level structure"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.db_client = None
        self.analyses_collection = None
        
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.db_client = MongoDBClient(self.db_config)
            await self.db_client.connect()
            # Access the raw collection for migration operations
            self.analyses_collection = self.db_client.db.analyses
            logger.info("✓ Connected to MongoDB")
        except Exception as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            raise
    
    async def extract_description(self, llm_response: Dict[str, Any]) -> Optional[str]:
        """Extract analysis description from llmResponse"""
        # Try different possible paths for description
        description = llm_response.get('analysis_description')
        if not description:
            description = llm_response.get('description')
        if not description:
            description = llm_response.get('analysis', {}).get('description')
        if not description:
            # Try to get from summary or other fields
            description = llm_response.get('summary')
        
        return description if description else None
    
    async def extract_parameters(self, llm_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract parameters from llmResponse.execution.parameters"""
        # Try different possible paths for parameters
        parameters = None
        
        # Path 1: llmResponse.execution.parameters
        if 'execution' in llm_response and 'parameters' in llm_response['execution']:
            parameters = llm_response['execution']['parameters']
        
        # Path 2: llmResponse.parameters
        elif 'parameters' in llm_response:
            parameters = llm_response['parameters']
        
        # Path 3: llmResponse.script_generation.parameters
        elif 'script_generation' in llm_response and 'parameters' in llm_response['script_generation']:
            parameters = llm_response['script_generation']['parameters']
        
        return parameters if parameters else None
    
    async def migrate_single_analysis(self, analysis: Dict[str, Any]) -> bool:
        """Migrate a single analysis record"""
        analysis_id = analysis.get('analysisId') or analysis.get('analysis_id')
        llm_response = analysis.get('llmResponse', {})
        
        if not llm_response:
            logger.debug(f"⚠️  Analysis {analysis_id} has no llmResponse - skipping")
            return False
        
        # Extract fields
        description = await self.extract_description(llm_response)
        parameters = await self.extract_parameters(llm_response)
        
        # Prepare update operations
        update_operations = {}
        changes_made = []
        
        # Add description if found and not already present at top level
        if description and not analysis.get('description'):
            update_operations['description'] = description
            changes_made.append('description')
        
        # Add parameters if found and not already present at top level
        if parameters and not analysis.get('parameters'):
            update_operations['parameters'] = parameters
            changes_made.append('parameters')
        
        # Update the analysis if we have changes
        if update_operations:
            try:
                result = await self.analyses_collection.update_one(
                    {"analysisId": analysis_id},
                    {"$set": update_operations}
                )
                
                if result.modified_count > 0:
                    logger.info(f"✓ Updated analysis {analysis_id}: {', '.join(changes_made)}")
                    return True
                else:
                    logger.warning(f"⚠️  Failed to update analysis {analysis_id}")
                    return False
                    
            except Exception as e:
                logger.error(f"✗ Error updating analysis {analysis_id}: {e}")
                return False
        else:
            logger.debug(f"ℹ️  No migration needed for analysis {analysis_id}")
            return False
    
    async def migrate_all_analyses(self) -> Dict[str, int]:
        """Migrate all analyses in the database"""
        stats = {
            'total': 0,
            'migrated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        logger.info("🚀 Starting migration of analysis fields...")
        
        try:
            # Get all analyses
            cursor = self.analyses_collection.find({})
            
            async for analysis in cursor:
                stats['total'] += 1
                
                try:
                    if await self.migrate_single_analysis(analysis):
                        stats['migrated'] += 1
                    else:
                        stats['skipped'] += 1
                        
                except Exception as e:
                    stats['errors'] += 1
                    analysis_id = analysis.get('analysisId', 'unknown')
                    logger.error(f"✗ Error migrating analysis {analysis_id}: {e}")
                
                # Progress logging
                if stats['total'] % 10 == 0:
                    logger.info(f"📊 Progress: {stats['total']} processed, {stats['migrated']} migrated")
        
        except Exception as e:
            logger.error(f"✗ Migration failed: {e}")
            stats['errors'] += 1
        
        return stats
    
    async def verify_migration(self) -> Dict[str, int]:
        """Verify migration results"""
        verification_stats = {
            'total_analyses': 0,
            'with_description': 0,
            'with_parameters': 0,
            'fully_migrated': 0
        }
        
        logger.info("🔍 Verifying migration results...")
        
        try:
            cursor = self.analyses_collection.find({})
            
            async for analysis in cursor:
                verification_stats['total_analyses'] += 1
                
                has_description = bool(analysis.get('description'))
                has_parameters = bool(analysis.get('parameters'))
                
                if has_description:
                    verification_stats['with_description'] += 1
                
                if has_parameters:
                    verification_stats['with_parameters'] += 1
                
                if has_description and has_parameters:
                    verification_stats['fully_migrated'] += 1
        
        except Exception as e:
            logger.error(f"✗ Verification failed: {e}")
        
        return verification_stats
    
    async def close(self):
        """Close database connection"""
        if self.db_client:
            await self.db_client.close()
            logger.info("✓ Database connection closed")


async def main():
    """Run the migration"""
    migrator = AnalysisFieldMigrator()
    
    try:
        # Initialize
        await migrator.initialize()
        
        # Run migration
        stats = await migrator.migrate_all_analyses()
        
        # Print results
        logger.info("📈 Migration Results:")
        logger.info(f"   Total analyses: {stats['total']}")
        logger.info(f"   Successfully migrated: {stats['migrated']}")
        logger.info(f"   Skipped (no changes needed): {stats['skipped']}")
        logger.info(f"   Errors: {stats['errors']}")
        
        # Verify migration
        verification = await migrator.verify_migration()
        logger.info("🔍 Post-migration verification:")
        logger.info(f"   Total analyses: {verification['total_analyses']}")
        logger.info(f"   With description field: {verification['with_description']}")
        logger.info(f"   With parameters field: {verification['with_parameters']}")
        logger.info(f"   Fully migrated: {verification['fully_migrated']}")
        
        success_rate = (stats['migrated'] / stats['total'] * 100) if stats['total'] > 0 else 0
        logger.info(f"✅ Migration completed with {success_rate:.1f}% success rate")
        
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        return 1
    
    finally:
        await migrator.close()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)