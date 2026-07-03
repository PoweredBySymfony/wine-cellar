const languageMenus =
  document.querySelectorAll<HTMLDetailsElement>('.language-menu')

document.addEventListener('click', (event) => {
  const target = event.target as Node
  languageMenus.forEach((menu) => {
    if (!menu.contains(target)) {
      menu.removeAttribute('open')
    }
  })
})

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') {
    return
  }
  languageMenus.forEach((menu) => {
    menu.removeAttribute('open')
  })
})
