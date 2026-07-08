const formModal = document.querySelector<HTMLDialogElement>('#form-modal')
let formModalSource: HTMLElement | null = null
let formModalReturnUrl = ''

const modalTitle = () =>
  formModal?.querySelector<HTMLElement>('[data-form-modal-title]')
const modalBody = () =>
  formModal?.querySelector<HTMLElement>('[data-form-modal-body]')

function closeFormModal() {
  if (!formModal?.open) {
    return
  }
  formModal.close()
  if (formModalReturnUrl) {
    window.history.replaceState({}, '', formModalReturnUrl)
  }
  formModalSource?.focus()
}

function syncAssetsFrom(doc: Document) {
  doc
    .querySelectorAll<HTMLLinkElement>('link[rel="stylesheet"][href]')
    .forEach((link) => {
      if (document.querySelector(`link[href="${link.href}"]`)) {
        return
      }
      document.head.append(link.cloneNode(true))
    })

  doc.querySelectorAll<HTMLScriptElement>('script[src]').forEach((script) => {
    if (document.querySelector(`script[src="${script.src}"]`)) {
      return
    }
    const nextScript = document.createElement('script')
    nextScript.src = script.src
    nextScript.defer = script.defer
    if (script.type) {
      nextScript.type = script.type
    }
    document.body.append(nextScript)
  })
}

function modalizeLinks(scope: ParentNode) {
  scope
    .querySelectorAll<HTMLAnchorElement>(
      '.wine-choose__card, a[href*="/wine/add/"], a[href*="/wine/ai/"], a[href*="/wine/edit/"], a[href*="/storage/add/"], a[href*="/storage/edit/"], a[href*="/stock/add/"], a[href*="/stock/edit/"], a[href*="/stock/open/"]'
    )
    .forEach((link) => {
      link.dataset.modalForm = 'true'
      link.setAttribute('aria-haspopup', 'dialog')
    })
}

function renderModalPage(html: string, url: string) {
  if (!formModal) {
    return
  }

  const doc = new DOMParser().parseFromString(html, 'text/html')
  syncAssetsFrom(doc)

  const headerTitle =
    doc.querySelector<HTMLElement>('.header__title')?.textContent?.trim() ||
    doc.querySelector('title')?.textContent?.trim() ||
    gettext('Edit')
  const main = doc.querySelector<HTMLElement>('main.main')
  const body = modalBody()
  const title = modalTitle()

  if (!main || !body || !title) {
    window.location.assign(url)
    return
  }

  title.textContent = headerTitle
  body.innerHTML = main.innerHTML
  modalizeLinks(body)
  window.history.replaceState({}, '', url)
  formModal.querySelector<HTMLButtonElement>('[data-form-modal-close]')?.focus()
  body.dispatchEvent(
    new CustomEvent('wine-cellar:modal-content', { bubbles: true })
  )
}

async function openFormModal(link: HTMLAnchorElement) {
  if (!formModal) {
    window.location.assign(link.href)
    return
  }

  formModalSource = link
  formModalReturnUrl = window.location.href
  const title = modalTitle()
  const body = modalBody()
  if (!title || !body) {
    window.location.assign(link.href)
    return
  }
  title.textContent = link.textContent?.trim() || gettext('Edit')
  body.innerHTML = `<div class="form-modal__loading" role="status">${gettext('Opening form…')}</div>`
  formModal.showModal()

  try {
    const response = await fetch(link.href, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    renderModalPage(await response.text(), response.url)
  } catch {
    window.location.assign(link.href)
  }
}

document.addEventListener('click', (event) => {
  const target = event.target as HTMLElement

  if (target.closest('[data-form-modal-close]')) {
    closeFormModal()
    return
  }

  const link = target.closest<HTMLAnchorElement>('[data-modal-form="true"]')
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey) {
    return
  }

  event.preventDefault()
  openFormModal(link)
})

document.addEventListener('submit', async (event) => {
  const form = event.target as HTMLFormElement
  if (!formModal?.open || !form.closest('[data-form-modal-body]')) {
    return
  }
  event.preventDefault()

  const submitter = (event as SubmitEvent).submitter as
    | HTMLButtonElement
    | HTMLInputElement
    | null
  const formData = submitter
    ? new FormData(form, submitter)
    : new FormData(form)
  const action = form.action || window.location.href
  modalBody()?.classList.add('is-loading')

  try {
    const response = await fetch(action, {
      method: form.method || 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
    if (response.redirected) {
      window.location.assign(response.url)
      return
    }
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    renderModalPage(await response.text(), response.url)
  } catch {
    form.submit()
  } finally {
    modalBody()?.classList.remove('is-loading')
  }
})

formModal?.addEventListener('click', (event) => {
  if (event.target === formModal) {
    closeFormModal()
  }
})

formModal?.addEventListener('cancel', (event) => {
  event.preventDefault()
  closeFormModal()
})

modalizeLinks(document)
