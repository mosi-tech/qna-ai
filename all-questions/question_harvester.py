#!/usr/bin/env python3
"""
Question Harvester - Consolidates all questions from all-questions directory
into a unified corpus with normalized metadata.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib


class QuestionHarvester:
    """Harvests and consolidates questions from multiple sources."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.consolidated_questions = []
        self.stats = {
            'duplicates': 0,
            'total_unique': 0,
            'sources': {}
        }
        self.question_hashes = set()  # For deduplication

    def get_file_hash(self, file_path: str) -> str:
        """Get hash of file content for deduplication."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return hashlib.md5(f.read().encode()).hexdigest()

    def normalize_question_text(self, text: str) -> str:
        """Normalize question text for deduplication."""
        # Remove extra whitespace and normalize
        normalized = ' '.join(text.strip().split())
        # Convert to lowercase for comparison
        return normalized.lower()

    def add_question(self, question: str, metadata: Dict[str, Any]) -> None:
        """Add a question with deduplication."""
        normalized = self.normalize_question_text(question)
        question_hash = hashlib.md5(normalized.encode()).hexdigest()

        if question_hash in self.question_hashes:
            self.stats['duplicates'] += 1
            return

        self.question_hashes.add(question_hash)
        self.consolidated_questions.append({
            'question': question,
            'normalized_text': normalized,
            'metadata': metadata
        })
        self.stats['total_unique'] += 1

    def harvest_sample_questions_openai(self) -> None:
        """Harvest from sample_questions_openai.json (array of question strings)."""
        file_path = self.base_dir / 'sample_questions_openai.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        self.stats['sources']['sample_questions_openai.json'] = len(questions)

        for question in questions:
            self.add_question(question, {
                'source_file': 'sample_questions_openai.json',
                'source_type': 'openai_sample',
                'category': 'account_portfolio',
                'status': 'unvalidated',
                'extraction_date': datetime.now().isoformat()
            })

    def harvest_valid_questions(self) -> None:
        """Harvest from valid_questions.json (array of validated question objects)."""
        file_path = self.base_dir / 'valid_questions.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data.get('valid_questions', [])

        self.stats['sources']['valid_questions.json'] = len(questions)

        for item in questions:
            question = item.get('question', '')
            metadata = {
                'source_file': 'valid_questions.json',
                'source_type': 'validated',
                'status': item.get('status', 'VALID'),
                'category': item.get('category', 'unknown'),
                'validation_notes': item.get('validation_notes', ''),
                'required_apis': item.get('required_apis', []),
                'data_requirements': item.get('data_requirements', []),
                'validation_date': item.get('validation_date', ''),
                'implementation_ready': item.get('implementation_ready', False),
                'extraction_date': datetime.now().isoformat()
            }
            self.add_question(question, metadata)

    def harvest_invalid_questions(self) -> None:
        """Harvest from invalid_questions.json (array of invalid question objects)."""
        file_path = self.base_dir / 'invalid_questions.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data.get('invalid_questions', [])

        self.stats['sources']['invalid_questions.json'] = len(questions)

        for item in questions:
            question = item.get('question', '')
            if not question:
                continue
            metadata = {
                'source_file': 'invalid_questions.json',
                'source_type': 'invalid',
                'status': 'INVALID',
                'rejection_reason': item.get('rejection_reason', ''),
                'missing_data': item.get('missing_data', []),
                'suggested_alternatives': item.get('suggested_alternatives', []),
                'validation_date': item.get('validation_date', ''),
                'category': item.get('category', ''),
                'extraction_date': datetime.now().isoformat()
            }
            self.add_question(question, metadata)

    def harvest_generated_questions(self) -> None:
        """Harvest from generated_questions.json."""
        file_path = self.base_dir / 'generated_questions.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data.get('questions', [])

        self.stats['sources']['generated_questions.json'] = len(questions)

        for question in questions:
            self.add_question(question, {
                'source_file': 'generated_questions.json',
                'source_type': 'generated',
                'category': 'generated',
                'status': 'unvalidated',
                'extraction_date': datetime.now().isoformat()
            })

    def harvest_processed_questions(self) -> None:
        """Harvest from processed_questions.json."""
        file_path = self.base_dir / 'processed_questions.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions = data.get('processed_questions', [])

        self.stats['sources']['processed_questions.json'] = len(questions)

        # Check if it has workflow or custom prefixes
        for question in questions:
            prefix = ''
            if question.startswith('CUSTOM:'):
                prefix = 'CUSTOM'
            elif question.startswith('WORKFLOW:'):
                prefix = 'WORKFLOW'

            metadata = {
                'source_file': 'processed_questions.json',
                'source_type': 'processed',
                'category': 'processed',
                'question_prefix': prefix if prefix else None,
                'status': 'processed',
                'extraction_date': datetime.now().isoformat()
            }

            # If there's a prefix, extract the clean question
            if prefix:
                metadata['question_text'] = question.replace(f'{prefix}: ', '')
                metadata['original_text'] = question
                self.add_question(metadata['question_text'], metadata)
            else:
                self.add_question(question, metadata)

    def harvest_questions_list(self) -> None:
        """Harvest from questions-list directory (individual .txt files)."""
        questions_list_dir = self.base_dir / 'questions-list'
        if not questions_list_dir.exists():
            return

        question_count = 0
        for txt_file in sorted(questions_list_dir.glob('*.txt'), key=lambda x: int(x.stem) if x.stem.isdigit() else x.stem):
            with open(txt_file, 'r', encoding='utf-8') as f:
                question = f.read().strip()

            if question:
                metadata = {
                    'source_file': f'questions-list/{txt_file.name}',
                    'source_type': 'individual_question',
                    'category': 'questions_list',
                    'question_id': txt_file.stem,
                    'status': 'unvalidated',
                    'extraction_date': datetime.now().isoformat()
                }
                self.add_question(question, metadata)
                question_count += 1

        self.stats['sources']['questions-list/'] = question_count

    def harvest_question_tree(self) -> None:
        """Harvest from question-tree directory (follow-up question trees)."""
        question_tree_dir = self.base_dir / 'question-tree'
        if not question_tree_dir.exists():
            return

        question_count = 0
        for json_file in question_tree_dir.glob('*.json'):
            if json_file.name == 'mcp-integration-prompt.md':
                continue

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract questions from tree structure
            root_question = data.get('root_question', '')
            if root_question:
                metadata = {
                    'source_file': f'question-tree/{json_file.name}',
                    'source_type': 'question_tree',
                    'category': data.get('description', 'follow-up tree'),
                    'tree_level': 'root',
                    'tree_id': json_file.stem,
                    'status': 'follow-up_question',
                    'extraction_date': datetime.now().isoformat()
                }
                self.add_question(root_question, metadata)
                question_count += 1

            # Extract questions from tree structure
            tree_structure = data.get('tree_structure', {})
            for level_name, level_data in tree_structure.items():
                for node_id, node_data in level_data.items():
                    question = node_data.get('question', '')
                    if question and question != root_question:
                        metadata = {
                            'source_file': f'question-tree/{json_file.name}',
                            'source_type': 'question_tree',
                            'category': node_data.get('category', ''),
                            'analysis_type': node_data.get('analysis_type', ''),
                            'tree_level': level_name,
                            'node_id': node_id,
                            'parent_node': node_data.get('parent', ''),
                            'tree_id': json_file.stem,
                            'rationale': node_data.get('rationale', ''),
                            'status': 'follow-up_question',
                            'extraction_date': datetime.now().isoformat()
                        }
                        self.add_question(question, metadata)
                        question_count += 1

        self.stats['sources']['question-tree/'] = question_count

    def harvest_stock_etf_info(self) -> None:
        """Harvest typical questions from stock-etf-info-category.json."""
        file_path = self.base_dir / 'stock-etf-info-category.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        question_count = 0
        analyses = data.get('analyses', [])
        for analysis in analyses:
            typical_questions = analysis.get('typical_questions', [])
            for question in typical_questions:
                metadata = {
                    'source_file': 'stock-etf-info-category.json',
                    'source_type': 'category_definition',
                    'category': analysis.get('category', ''),
                    'analysis_id': analysis.get('analysis_id', ''),
                    'complexity': analysis.get('complexity', ''),
                    'status': 'categorized',
                    'extraction_date': datetime.now().isoformat()
                }
                self.add_question(question, metadata)
                question_count += 1

        self.stats['sources']['stock-etf-info-category.json'] = question_count

    def harvest_portfolio_visualizer_analyses(self) -> None:
        """Harvest typical questions from portfolio-visualizer-analyses.json."""
        file_path = self.base_dir / 'portfolio-visualizer-analyses.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        question_count = 0
        analyses = data.get('analyses', [])
        for analysis in analyses:
            typical_questions = analysis.get('typical_questions', [])
            for question in typical_questions:
                metadata = {
                    'source_file': 'portfolio-visualizer-analyses.json',
                    'source_type': 'portfolio_visualizer',
                    'category': analysis.get('category', ''),
                    'analysis_id': analysis.get('analysis_id', ''),
                    'complexity': analysis.get('complexity', ''),
                    'status': 'portfolio_analysis',
                    'extraction_date': datetime.now().isoformat()
                }
                self.add_question(question, metadata)
                question_count += 1

        self.stats['sources']['portfolio-visualizer-analyses.json'] = question_count

    def harvest_portfolio_visualizer_simple_enhanced(self) -> None:
        """Harvest typical questions from portfolio-visualizer-simple-enhanced.json."""
        file_path = self.base_dir / 'portfolio-visualizer-simple-enhanced.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        question_count = 0
        analyses = data.get('analyses', [])
        for analysis in analyses:
            typical_questions = analysis.get('typical_questions', [])
            for question in typical_questions:
                metadata = {
                    'source_file': 'portfolio-visualizer-simple-enhanced.json',
                    'source_type': 'portfolio_visualizer_enhanced',
                    'category': analysis.get('category', ''),
                    'analysis_id': analysis.get('analysis_id', ''),
                    'complexity': analysis.get('complexity', ''),
                    'status': 'portfolio_analysis',
                    'extraction_date': datetime.now().isoformat()
                }
                self.add_question(question, metadata)
                question_count += 1

        self.stats['sources']['portfolio-visualizer-simple-enhanced.json'] = question_count

    def harvest_questions_old_combined(self) -> None:
        """Harvest from questions_old/combined.json."""
        file_path = self.base_dir / 'questions_old' / 'combined.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            queries = data.get('queries', [])

        question_count = 0
        for query in queries:
            question = query.get('question', '')
            if question:
                metadata = {
                    'source_file': 'questions_old/combined.json',
                    'source_type': 'old_combined',
                    'category': query.get('category', ''),
                    'symbols': query.get('symbols', []),
                    'function': query.get('function', ''),
                    'status': 'archived',
                    'extraction_date': datetime.now().isoformat()
                }
                self.add_question(question, metadata)
                question_count += 1

        self.stats['sources']['questions_old/combined.json'] = question_count

    def harvest_retail_analysis_tools(self) -> None:
        """Harvest user_questions from retail-analysis-tools-registry.json."""
        file_path = self.base_dir / 'retail-analysis-tools-registry.json'
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        question_count = 0
        # Navigate through tier structure to find user_questions
        for tier_key, tier_data in data.items():
            if isinstance(tier_data, dict) and 'tools' in tier_data:
                for tool in tier_data['tools']:
                    user_questions = tool.get('user_questions', [])
                    for question in user_questions:
                        metadata = {
                            'source_file': 'retail-analysis-tools-registry.json',
                            'source_type': 'retail_analysis_tool',
                            'category': tool.get('id', ''),
                            'tool_name': tool.get('name', ''),
                            'complexity': tool.get('complexity', ''),
                            'status': 'tool_definition',
                            'extraction_date': datetime.now().isoformat()
                        }
                        self.add_question(question, metadata)
                        question_count += 1

        self.stats['sources']['retail-analysis-tools-registry.json'] = question_count

    def harvest_comprehensive_retail_analysis_tools(self) -> None:
        """Harvest from comprehensive-retail-analysis-tools.json."""
        file_path = self.base_dir / 'comprehensive-retail-analysis-tools.json'
        if not file_path.exists():
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  Warning: JSON parse error in comprehensive-retail-analysis-tools.json: {e}")
            return

        question_count = 0
        # Navigate through tier structure to find tools with user_questions
        for tier_key, tier_data in data.items():
            if isinstance(tier_data, dict) and 'tools' in tier_data:
                for tool in tier_data['tools']:
                    # Check for typical_questions in parameters
                    inputs = tool.get('inputs', {})
                    if isinstance(inputs, dict):
                        for key, value in inputs.items():
                            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
                                # This might be questions, check if it's user_questions
                                if key == 'user_questions' or 'question' in key.lower():
                                    for question in value:
                                        metadata = {
                                            'source_file': 'comprehensive-retail-analysis-tools.json',
                                            'source_type': 'comprehensive_retail_tool',
                                            'category': tool.get('id', ''),
                                            'tool_name': tool.get('name', ''),
                                            'complexity': tool.get('complexity', ''),
                                            'status': 'tool_definition',
                                            'extraction_date': datetime.now().isoformat()
                                        }
                                        self.add_question(question, metadata)
                                        question_count += 1

        self.stats['sources']['comprehensive-retail-analysis-tools.json'] = question_count

    def harvest_all(self) -> None:
        """Harvest questions from all sources."""
        print("Starting question harvest...")
        print()

        self.harvest_sample_questions_openai()
        print(f"Harvested from: sample_questions_openai.json")

        self.harvest_valid_questions()
        print(f"Harvested from: valid_questions.json")

        self.harvest_invalid_questions()
        print(f"Harvested from: invalid_questions.json")

        self.harvest_generated_questions()
        print(f"Harvested from: generated_questions.json")

        self.harvest_processed_questions()
        print(f"Harvested from: processed_questions.json")

        self.harvest_questions_list()
        print(f"Harvested from: questions-list/")

        self.harvest_question_tree()
        print(f"Harvested from: question-tree/")

        self.harvest_stock_etf_info()
        print(f"Harvested from: stock-etf-info-category.json")

        self.harvest_portfolio_visualizer_analyses()
        print(f"Harvested from: portfolio-visualizer-analyses.json")

        self.harvest_portfolio_visualizer_simple_enhanced()
        print(f"Harvested from: portfolio-visualizer-simple-enhanced.json")

        self.harvest_questions_old_combined()
        print(f"Harvested from: questions_old/combined.json")

        self.harvest_retail_analysis_tools()
        print(f"Harvested from: retail-analysis-tools-registry.json")

        self.harvest_comprehensive_retail_analysis_tools()
        print(f"Harvested from: comprehensive-retail-analysis-tools.json")

        print()
        print("Harvest complete!")

    def generate_statistics(self) -> Dict[str, Any]:
        """Generate statistics about the consolidated questions."""
        # Count by status
        status_counts = {}
        category_counts = {}
        source_type_counts = {}

        for q in self.consolidated_questions:
            status = q['metadata'].get('status', 'unknown')
            category = q['metadata'].get('category', 'unknown')
            source_type = q['metadata'].get('source_type', 'unknown')

            status_counts[status] = status_counts.get(status, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1

        return {
            'total_unique_questions': len(self.consolidated_questions),
            'duplicates_removed': self.stats['duplicates'],
            'questions_by_source': dict(self.stats['sources']),
            'questions_by_status': status_counts,
            'questions_by_category': category_counts,
            'questions_by_source_type': source_type_counts,
            'consolidation_date': datetime.now().isoformat()
        }

    def save_consolidated_questions(self, output_file: str) -> None:
        """Save consolidated questions to JSON file."""
        stats = self.generate_statistics()

        output_data = {
            'statistics': stats,
            'questions': self.consolidated_questions
        }

        output_path = self.base_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print()
        print(f"Consolidated questions saved to: {output_file}")
        print()
        print("=== STATISTICS ===")
        print(f"Total unique questions: {stats['total_unique_questions']}")
        print(f"Duplicates removed: {stats['duplicates_removed']}")
        print()
        print("Questions by source:")
        for source, count in sorted(stats['questions_by_source'].items()):
            print(f"  {source}: {count}")
        print()
        print("Questions by status:")
        for status, count in sorted(stats['questions_by_status'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count}")
        print()
        print("Questions by source type:")
        for source_type, count in sorted(stats['questions_by_source_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {source_type}: {count}")


def main():
    """Main entry point."""
    base_dir = '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/all-questions'
    output_file = 'consolidated_questions.json'

    harvester = QuestionHarvester(base_dir)
    harvester.harvest_all()
    harvester.save_consolidated_questions(output_file)


if __name__ == '__main__':
    main()