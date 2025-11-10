import type { EarningsMaterial } from '../types'
import './MaterialsList.css'

interface MaterialsListProps {
  materials: EarningsMaterial[]
}

export const MaterialsList = ({ materials }: MaterialsListProps) => {
  // 年度ごとにグループ化
  const groupedByYear = materials.reduce((acc, material) => {
    const year = material.fiscal_year
    if (!acc[year]) {
      acc[year] = []
    }
    acc[year].push(material)
    return acc
  }, {} as Record<string, EarningsMaterial[]>)

  // 年度を降順にソート
  const sortedYears = Object.keys(groupedByYear).sort((a, b) => {
    const yearA = parseInt(a.replace(/\D/g, ''))
    const yearB = parseInt(b.replace(/\D/g, ''))
    return yearB - yearA
  })

  return (
    <div className="materials-list">
      {sortedYears.map((year) => (
        <div key={year} className="year-section">
          <h3 className="year-header">{year}</h3>
          <div className="materials-grid">
            {groupedByYear[year].map((material, index) => (
              <div key={index} className="material-card">
                <div className="material-header">
                  <span className={`material-type ${material.type === '決算短信' ? 'type-summary' : 'type-presentation'}`}>
                    {material.type}
                  </span>
                  <span className="material-period">{material.period}</span>
                </div>

                <h4 className="material-title">{material.title}</h4>

                <div className="material-meta">
                  <div className="meta-item">
                    <span className="meta-label">発表日:</span>
                    <span className="meta-value">{formatDate(material.announcement_date)}</span>
                  </div>
                </div>

                <a
                  href={material.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="material-link"
                >
                  <svg
                    className="pdf-icon"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                      clipRule="evenodd"
                    />
                  </svg>
                  資料を開く
                </a>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}
