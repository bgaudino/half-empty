for (const toggle of document.querySelectorAll('[data-toggle]')) {
  toggle.onclick = function () {
    for (const element of document.querySelectorAll(toggle.dataset.toggle)) {
      if (element.classList.contains('u-hide')) {
        element.classList.remove('u-hide');
        toggle.querySelector('span').innerText = toggle.dataset.hideText;
        toggle.querySelector('i').className = 'p-icon--chevron-down';
      } else {
        element.classList.add('u-hide');
        toggle.querySelector('span').innerText = toggle.dataset.showText;
        toggle.querySelector('i').className = 'p-icon--chevron-up';
      }
    }
  };
}
