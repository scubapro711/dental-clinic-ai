import { useState, useEffect, useRef, RefObject } from 'react'

/**
 * Hook that measures the width of an HTML element and updates when it changes
 * This is a replacement for WidthProvider which has issues with measureBeforeMount
 * 
 * @param ref - React ref to the element to measure
 * @returns The current width of the element, or null if not yet measured
 */
export function useElementWidth(ref: RefObject<HTMLElement>): number | null {
  const [width, setWidth] = useState<number | null>(null)

  useEffect(() => {
    if (!ref.current) return

    // Initial measurement
    const updateWidth = () => {
      if (ref.current) {
        setWidth(ref.current.offsetWidth)
      }
    }

    // Measure immediately
    updateWidth()

    // Create ResizeObserver to watch for size changes
    const resizeObserver = new ResizeObserver(() => {
      updateWidth()
    })

    resizeObserver.observe(ref.current)

    // Also listen to window resize as fallback
    window.addEventListener('resize', updateWidth)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('resize', updateWidth)
    }
  }, [ref])

  return width
}
