const passwordFields = document.querySelectorAll<HTMLInputElement>(
  'input[type="password"]'
)

passwordFields.forEach((field) => {
  let wrapper = field.closest<HTMLElement>('.password-field')
  if (!wrapper) {
    wrapper = document.createElement('span')
    wrapper.className = 'password-field'
    field.parentNode?.insertBefore(wrapper, field)
    wrapper.appendChild(field)
  }

  let button = wrapper.querySelector<HTMLButtonElement>(
    '[data-password-toggle]'
  )
  if (!button) {
    button = document.createElement('button')
    button.type = 'button'
    button.className = 'password-field__toggle'
    button.dataset.passwordToggle = ''
    button.setAttribute('aria-label', gettext('Show password'))
    button.setAttribute('aria-pressed', 'false')
    button.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"></path><circle cx="12" cy="12" r="2.5"></circle></svg>'
    wrapper.appendChild(button)
  }

  button.addEventListener('click', () => {
    const isVisible = field.type === 'text'
    field.type = isVisible ? 'password' : 'text'
    button.setAttribute('aria-pressed', String(!isVisible))
    button.setAttribute(
      'aria-label',
      isVisible ? gettext('Show password') : gettext('Hide password')
    )
  })
})
