const panel = document.querySelector<HTMLDialogElement>('#wine-detail-panel')
let sourceLink: HTMLAnchorElement | null = null
let listUrl = ''

const closePanel = () => {
  if (!panel?.open) {
    return
  }
  panel.close()
  if (listUrl) {
    window.history.replaceState({}, '', listUrl)
  }
  sourceLink?.focus()
}

document.addEventListener('click', async (event) => {
  const target = event.target as HTMLElement
  const link = target.closest<HTMLAnchorElement>('[data-wine-panel-url]')

  if (target.closest('[data-wine-panel-close]')) {
    closePanel()
    return
  }

  if (!link || !panel || event.ctrlKey || event.metaKey || event.shiftKey) {
    return
  }
  event.preventDefault()
  sourceLink = link
  listUrl = window.location.href
  panel.innerHTML = `<div class="wine-panel__loading" role="status">${gettext('Opening wine details…')}</div>`
  panel.showModal()

  try {
    const response = await fetch(link.dataset.winePanelUrl || link.href, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    panel.innerHTML = await response.text()
    window.history.replaceState({}, '', link.href)
    panel.querySelector<HTMLElement>('[data-wine-panel-close]')?.focus()
  } catch {
    panel.close()
    window.location.assign(link.href)
  }
})

panel?.addEventListener('click', (event) => {
  if (event.target === panel) {
    closePanel()
  }
})

panel?.addEventListener('cancel', (event) => {
  event.preventDefault()
  closePanel()
})
