(function () {
  function markChallengePage() {
    document.documentElement.classList.toggle(
      "terminal-challenges",
      window.location.pathname.replace(/\/+$/, "") === "/challenges",
    );
  }

  markChallengePage();
  window.addEventListener("popstate", markChallengePage);

  var pushState = history.pushState;
  history.pushState = function () {
    var result = pushState.apply(this, arguments);
    setTimeout(markChallengePage, 0);
    return result;
  };

  var replaceState = history.replaceState;
  history.replaceState = function () {
    var result = replaceState.apply(this, arguments);
    setTimeout(markChallengePage, 0);
    return result;
  };
})();
