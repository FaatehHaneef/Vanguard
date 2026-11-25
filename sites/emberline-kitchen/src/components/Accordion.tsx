import { type ReactNode, useId, useState } from 'react'
import { Icon } from './Icon'

export interface AccordionItem {
  title: string
  body: ReactNode
}

export function Accordion({ items }: { items: AccordionItem[] }) {
  const [open, setOpen] = useState<number | null>(null)
  const id = useId()
  return (
    <div className="accordion">
      {items.map((item, index) => {
        const expanded = open === index
        return (
          <div className="accordion-item" key={item.title}>
            <h3>
              <button
                type="button"
                className="accordion-trigger"
                id={`${id}-t${index}`}
                aria-expanded={expanded}
                aria-controls={`${id}-p${index}`}
                onClick={() => setOpen(expanded ? null : index)}
              >
                {item.title}
                <Icon name="chevron-down" />
              </button>
            </h3>
            {expanded && (
              <div
                className="accordion-panel"
                id={`${id}-p${index}`}
                role="region"
                aria-labelledby={`${id}-t${index}`}
              >
                {item.body}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
