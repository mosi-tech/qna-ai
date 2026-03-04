/**
 * DecisionBlock
 * 
 * Description: Pros/cons analysis with recommendation rationale
 * Use Cases: Investment decisions, strategic choices, option evaluation
 * Data Format: Pros, cons, recommendation, and supporting rationale
 * 
 * @param decision - Decision being analyzed
 * @param pros - Array of positive factors
 * @param cons - Array of negative factors
 * @param recommendation - Final recommendation
 * @param rationale - Supporting reasoning
 * @param confidence - Confidence level in recommendation
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { insightStyles, cn } from './shared/styles';

interface DecisionFactor {
  text: string;
  weight?: 'high' | 'medium' | 'low';
  impact?: string;
}

interface DecisionBlockProps {
  decision: string;
  pros: (string | DecisionFactor)[];
  cons: (string | DecisionFactor)[];
  recommendation: string;
  rationale: string;
  confidence?: 'high' | 'medium' | 'low';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function DecisionBlock({ 
  decision,
  pros,
  cons,
  recommendation,
  rationale,
  confidence = 'medium',
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: DecisionBlockProps) {
  
  const getConfidenceColor = () => {
    switch (confidence) {
      case 'high':
        return cn(insightStyles.status.success.text, insightStyles.status.success.bgMedium);
      case 'low':
        return cn(insightStyles.status.error.text, insightStyles.status.error.bgMedium);
      case 'medium':
      default:
        return cn(insightStyles.status.warning.text, insightStyles.status.warning.bgMedium);
    }
  };

  const getWeightColor = (weight: string = 'medium') => {
    switch (weight) {
      case 'high':
        return insightStyles.status.error.textLight;
      case 'low':
        return insightStyles.text.tertiary;
      case 'medium':
      default:
        return insightStyles.text.secondary;
    }
  };

  const getWeightIcon = (weight: string = 'medium') => {
    switch (weight) {
      case 'high':
        return '●●●';
      case 'low':
        return '●○○';
      case 'medium':
      default:
        return '●●○';
    }
  };

  const renderFactor = (factor: string | DecisionFactor, index: number, isPositive: boolean) => {
    const text = typeof factor === 'string' ? factor : factor.text;
    const weight = typeof factor === 'string' ? 'medium' : factor.weight;
    const impact = typeof factor === 'string' ? undefined : factor.impact;

    return (
      <li key={index} className="flex items-start space-x-3">
        <div className={cn(
          'w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0',
          isPositive ? insightStyles.status.success.accent : insightStyles.status.error.accent
        )}></div>
        <div className="flex-1">
          <p className={cn('text-sm', getWeightColor(weight))}>
            {text}
          </p>
          {variant === 'detailed' && (weight !== 'medium' || impact) && (
            <div className={cn('mt-1 flex gap-3 text-xs', insightStyles.text.tertiary)}>
              {weight !== 'medium' && (
                <span>Weight: {getWeightIcon(weight)}</span>
              )}
              {impact && (
                <span>Impact: {impact}</span>
              )}
            </div>
          )}
        </div>
      </li>
    );
  };
  
  return (
    <div className={cn(insightStyles.card.base, insightStyles.spacing.component)}>
      <div className={insightStyles.spacing.margin}>
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 mb-2">
          <h3 className={insightStyles.typography.h3}>{decision}</h3>
          <span className={cn('px-3 py-1 text-xs font-medium rounded-full', getConfidenceColor())}>
            {confidence} confidence
          </span>
        </div>
      </div>
      
      <div className={cn(insightStyles.grid.cols2, insightStyles.spacing.gap, 'mb-6')}>
        {/* Pros */}
        <div className={cn(
          insightStyles.status.success.bg, 
          insightStyles.status.success.border, 
          'rounded-lg p-4'
        )}>
          <h4 className={cn(insightStyles.typography.h4, insightStyles.status.success.text, 'mb-3 flex items-center')}>
            <span className="mr-2">✓</span>
            Pros ({pros.length})
          </h4>
          <ul className="space-y-3">
            {pros.map((pro, index) => renderFactor(pro, index, true))}
          </ul>
        </div>
        
        {/* Cons */}
        <div className={cn(
          insightStyles.status.error.bg, 
          insightStyles.status.error.border, 
          'rounded-lg p-4'
        )}>
          <h4 className={cn(insightStyles.typography.h4, insightStyles.status.error.text, 'mb-3 flex items-center')}>
            <span className="mr-2">✗</span>
            Cons ({cons.length})
          </h4>
          <ul className="space-y-3">
            {cons.map((con, index) => renderFactor(con, index, false))}
          </ul>
        </div>
      </div>
      
      {/* Recommendation */}
      <div className={cn(
        insightStyles.status.info.bg, 
        insightStyles.status.info.border, 
        'rounded-lg p-4 mb-4'
      )}>
        <h4 className={cn(insightStyles.typography.h4, insightStyles.status.info.text, 'mb-2 flex items-center')}>
          <span className="mr-2">🎯</span>
          Recommendation
        </h4>
        <p className={cn('text-sm font-medium mb-2', insightStyles.status.info.text)}>
          {recommendation}
        </p>
        <p className={cn('text-sm leading-relaxed', insightStyles.status.info.textLight)}>
          {rationale}
        </p>
      </div>

      {/* Decision Summary */}
      {variant === 'detailed' && (
        <div className={cn(insightStyles.surface.secondary, 'rounded-lg p-4 mb-4')}>
          <h5 className={cn('text-sm font-medium mb-2', insightStyles.text.primary)}>Decision Summary</h5>
          <div className={cn(insightStyles.grid.cols3, insightStyles.spacing.gapSmall, 'text-center text-sm')}>
            <div>
              <div className={cn('font-semibold', insightStyles.status.success.textLight)}>{pros.length}</div>
              <div className={insightStyles.text.secondary}>Positive Factors</div>
            </div>
            <div>
              <div className={cn('font-semibold', insightStyles.status.error.textLight)}>{cons.length}</div>
              <div className={insightStyles.text.secondary}>Negative Factors</div>
            </div>
            <div>
              <div className={cn('font-semibold', 
                confidence === 'high' ? insightStyles.status.success.textLight :
                confidence === 'low' ? insightStyles.status.error.textLight : insightStyles.status.warning.textLight
              )}>
                {confidence.toUpperCase()}
              </div>
              <div className={insightStyles.text.secondary}>Confidence</div>
            </div>
          </div>
        </div>
      )}
      
      {(onApprove || onDisapprove) && (
        <div className={cn('flex gap-2 pt-4', insightStyles.border.divider)}>
          {onApprove && (
            <button
              onClick={onApprove}
              className={insightStyles.button.approve.base}
            >
              Approve Decision
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className={insightStyles.button.disapprove.base}
            >
              Disapprove Decision
            </button>
          )}
        </div>
      )}
    </div>
  );
}