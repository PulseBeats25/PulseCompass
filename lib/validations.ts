import { z } from 'zod';

// Job schemas
export const JobStatusSchema = z.object({
  job_id: z.string().uuid(),
  status: z.enum(['queued', 'started', 'finished', 'failed']),
  result: z.any().optional(),
  error: z.string().optional(),
});

export const JobEnqueueResponseSchema = z.object({
  job_id: z.string().uuid(),
});

// Portfolio schemas
export const PortfolioPositionSchema = z.object({
  id: z.string(),
  company_name: z.string(),
  ticker: z.string(),
  shares: z.number().positive(),
  avg_cost: z.number().positive(),
  current_price: z.number().positive(),
  total_value: z.number(),
  gain_loss: z.number(),
  gain_loss_pct: z.number(),
});

export const PortfolioSchema = z.object({
  total_value: z.number(),
  total_cost: z.number(),
  total_gain_loss: z.number(),
  total_gain_loss_pct: z.number(),
  positions: z.array(PortfolioPositionSchema),
});

// Company schemas
export const CompanySchema = z.object({
  id: z.string(),
  name: z.string(),
  ticker: z.string(),
  sector: z.string().optional(),
  market_cap: z.number().optional(),
});

export const WatchlistSchema = z.object({
  companies: z.array(CompanySchema),
});

// Analysis schemas
export const FinancialMetricSchema = z.object({
  name: z.string(),
  value: z.union([z.number(), z.string()]),
  status: z.enum(['good', 'warning', 'bad']),
});

export const InvestorViewSchema = z.object({
  investor: z.string(),
  perspective: z.string(),
  key_points: z.array(z.string()),
  rating: z.number().min(1).max(10),
});

export const RecommendationSchema = z.object({
  action: z.enum(['buy', 'hold', 'sell']),
  confidence: z.number().min(0).max(100),
  reasoning: z.string(),
  target_price: z.number().optional(),
});

export const CompanyAnalysisSchema = z.object({
  company_id: z.string(),
  company_name: z.string(),
  financial_metrics: z.array(FinancialMetricSchema),
  investor_views: z.array(InvestorViewSchema),
  recommendation: RecommendationSchema,
  valuation_score: z.number().min(0).max(100),
  updated_at: z.string().datetime(),
});

// Upload schemas
export const UploadResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  files: z.array(z.object({
    file_id: z.string(),
    filename: z.string(),
    status: z.string(),
  })),
});

// Health check schemas
export const HealthCheckSchema = z.object({
  ok: z.boolean(),
  error: z.string().optional(),
});

// Metrics schemas
export const QueueMetricsSchema = z.object({
  timestamp: z.string(),
  queues: z.record(z.object({
    name: z.string(),
    count: z.number(),
    started_count: z.number(),
    finished_count: z.number(),
    failed_count: z.number(),
  })),
});

// Type exports
export type JobStatus = z.infer<typeof JobStatusSchema>;
export type JobEnqueueResponse = z.infer<typeof JobEnqueueResponseSchema>;
export type Portfolio = z.infer<typeof PortfolioSchema>;
export type Company = z.infer<typeof CompanySchema>;
export type CompanyAnalysis = z.infer<typeof CompanyAnalysisSchema>;
export type UploadResponse = z.infer<typeof UploadResponseSchema>;
export type HealthCheck = z.infer<typeof HealthCheckSchema>;
export type QueueMetrics = z.infer<typeof QueueMetricsSchema>;
