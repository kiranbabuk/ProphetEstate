export interface ValuationData {
  estimatedValue: number
  confidence: number
  comparables: Array<{
    address: string
    price: number
    soldDate: string
    similarity: number
  }>
  marketTrends: {
    yearlyAppreciation: number
    averageDaysOnMarket: number
    pricePerSqft: number
  }
}