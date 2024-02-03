function isExpanded(element) {
  return element.ariaExpanded === 'true';
}

function expandMenu(element) {
  element.ariaExpanded = 'true';
  document.getElementById(element.getAttribute('aria-controls')).ariaHidden =
    'false';
}

function toggleMenu(element) {
  isExpanded(element) ? hideMenu(element) : expandMenu(element);
}

function hideMenu(element) {
  element.ariaExpanded = 'false';
  document.getElementById(element.getAttribute('aria-controls')).ariaHidden =
    'true';
}

function hideAll(element) {
  for (const el of document.querySelectorAll(
    '.p-contextual-menu__toggle, [aria-expanded="true"]'
  )) {
    if (element !== el) {
      hideMenu(el);
    }
  }
}

for (const element of document.querySelectorAll('.p-contextual-menu__toggle')) {
  element.onclick = function (e) {
    e.stopPropagation();
    toggleMenu(element);
    hideAll(element);
  };
}

document.onclick = () => hideAll();
