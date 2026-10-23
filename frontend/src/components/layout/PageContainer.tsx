import type { ReactNode } from 'react'

export default function PageContainer({ children, eyebrow, title, description, action }: {
  children: ReactNode
  eyebrow?: string
  title: ReactNode
  description?: string
  action?: ReactNode
}) {
  return <div className="page-container">
    <div className="section-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {description && <p className="subtitle">{description}</p>}
      </div>
      {action}
    </div>
    {children}
  </div>
}
