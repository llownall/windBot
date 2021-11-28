document
  .querySelectorAll('button.delete_button[data-url]')
  .forEach(el => {
    el.addEventListener('click', () => {
      let isConfirmed = confirm('Ты уверен?')
      if (isConfirmed) {
        window.location.href = el.dataset.url
      }
    })
  })