export interface EarningsMaterial {
  title: string
  company_name: string
  stock_code: string
  fiscal_year: string
  period: string
  announcement_date: string
  pdf_url: string
  type: string
}

export interface ApiResponse {
  stock_code: string
  materials: EarningsMaterial[]
}

export interface ApiError {
  error: string
  stock_code?: string
}
