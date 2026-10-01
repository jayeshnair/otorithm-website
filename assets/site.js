/* Otorithm site behaviour: constellations, navigation, copy buttons, contact form. */
(function () {
  'use strict';

  /* ---------- Constellations ---------- */
  var css = getComputedStyle(document.documentElement);
  var token = function (name, fallback) { return (css.getPropertyValue(name) || '').trim() || fallback; };
  if (window.Constellation) {
    document.querySelectorAll('canvas[data-formation]').forEach(function (canvas) {
      new window.Constellation(canvas, {
        color: token('--fg', '#111418'),
        accent: token('--accent', '#c27a2c'),
        formation: canvas.getAttribute('data-formation'),
        ambient: Number(canvas.getAttribute('data-ambient') || 0),
        fill: Number(canvas.getAttribute('data-fill') || 0.72),
        radius: Number(canvas.getAttribute('data-radius') || 0) || undefined,
        force: Number(canvas.getAttribute('data-force') || 0) || undefined,
        swirl: Number(canvas.getAttribute('data-swirl') || 0) || undefined,
        ease: Number(canvas.getAttribute('data-ease') || 0) || undefined,
      });
    });
  }

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Hero video: plays only while visible; off for reduced motion ---------- */
  var video = document.getElementById('hero-video');
  var toggle = document.getElementById('video-toggle');
  if (video) {
    var userPaused = reduceMotion;
    var inView = true;
    video.muted = true;
    var play = function () {
      var pr = video.play();
      if (pr && pr.catch) pr.catch(function () { /* autoplay refused: poster stays */ });
    };
    var sync = function () {
      if (!userPaused && inView) play(); else video.pause();
      if (toggle) {
        toggle.textContent = userPaused ? 'Play background' : 'Pause background';
        toggle.setAttribute('aria-pressed', String(userPaused));
      }
    };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        sync();
      }).observe(video);
    }
    if (toggle) toggle.addEventListener('click', function () { userPaused = !userPaused; sync(); });
    sync();
  }

  /* ---------- Typewriter ---------- */
  document.querySelectorAll('[data-typewriter]').forEach(function (el) {
    var text = el.getAttribute('data-typewriter');
    var out = el.querySelector('.typed-text');
    if (!out) return;
    if (reduceMotion) { out.textContent = text; return; }
    var i = 0;
    setTimeout(function () {
      var id = setInterval(function () {
        i += 1;
        out.textContent = text.slice(0, i);
        if (i >= text.length) clearInterval(id);
      }, 36);
    }, 700);
  });

  /* ---------- Nav background once scrolled ---------- */
  var nav = document.querySelector('.nav');
  if (nav) {
    var onScroll = function () { nav.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Mobile menu ---------- */
  var burger = document.getElementById('burger');
  var menu = document.getElementById('menu');
  if (burger && menu) {
    var links = menu.querySelectorAll('a');
    var onKey = function (e) { if (e.key === 'Escape') setMenu(false); };
    var setMenu = function (open) {
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      menu.classList.toggle('open', open);
      menu.setAttribute('aria-hidden', String(!open));
      links.forEach(function (a) { a.tabIndex = open ? 0 : -1; });
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) window.addEventListener('keydown', onKey);
      else window.removeEventListener('keydown', onKey);
    };
    burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
    links.forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  }

  /* ---------- Copy-to-clipboard buttons ---------- */
  var status = document.getElementById('live-status');
  var announce = function (msg) { if (status) status.textContent = msg; };
  var selectText = function (el) {
    try {
      var range = document.createRange();
      range.selectNodeContents(el);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    } catch (e) { /* selection not available */ }
  };
  var copyText = function (text, onDone, onFail) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(onDone, onFail);
    } else {
      onFail();
    }
  };
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    var labelEl = btn.querySelector('[data-copy-label]') || btn;
    var original = labelEl.textContent;
    var timer = null;
    btn.addEventListener('click', function () {
      var value = btn.getAttribute('data-copy');
      copyText(value, function () {
        labelEl.textContent = 'Copied';
        announce(value + ' copied to clipboard');
        clearTimeout(timer);
        timer = setTimeout(function () { labelEl.textContent = original; announce(''); }, 1600);
      }, function () {
        selectText(labelEl);
        announce('Press Ctrl+C or Cmd+C to copy ' + value);
      });
    });
  });

  /* ---------- Contact form ---------- */
  var form = document.getElementById('contact-form');
  if (form) {
    var result = document.getElementById('form-result');
    var endpoint = form.getAttribute('data-endpoint') || '';
    var email = form.getAttribute('data-email') || 'contact@otorithm.com';

    var compose = function (d) {
      return [
        'Name: ' + d.name,
        'Email: ' + d.email,
        'Company: ' + (d.company || '-'),
        'Interested in: ' + d.interest,
        '',
        d.message,
      ].join('\n');
    };

    var showFallback = function (d, lead) {
      var body = compose(d);
      var subject = 'Enquiry: ' + d.interest;
      result.hidden = false;
      result.innerHTML = '';
      var p = document.createElement('p');
      p.className = 'small';
      p.textContent = lead + ' Copy it and send it to ' + email + ', and an engineer will reply.';
      var ta = document.createElement('textarea');
      ta.readOnly = true;
      ta.id = 'composed-message';
      ta.setAttribute('aria-label', 'Your composed message');
      ta.value = body;
      var row = document.createElement('div');
      row.className = 'actions';
      var copyBtn = document.createElement('button');
      copyBtn.type = 'button';
      copyBtn.className = 'btn btn-sm';
      copyBtn.textContent = 'Copy message';
      copyBtn.addEventListener('click', function () {
        copyText(body, function () {
          copyBtn.textContent = 'Copied';
          setTimeout(function () { copyBtn.textContent = 'Copy message'; }, 1600);
        }, function () { ta.focus(); ta.select(); });
      });
      var mail = document.createElement('a');
      mail.className = 'ghost';
      mail.href = 'mailto:' + email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      mail.innerHTML = 'Open in your email app <span class="arrow" aria-hidden="true">→</span>';
      row.appendChild(copyBtn);
      row.appendChild(mail);
      result.appendChild(p);
      result.appendChild(ta);
      result.appendChild(row);
      result.focus();
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var d = {
        name: form.elements.name.value.trim(),
        email: form.elements.email.value.trim(),
        company: form.elements.company.value.trim(),
        interest: form.elements.interest.value,
        message: form.elements.message.value.trim(),
      };
      if (!endpoint) {
        showFallback(d, 'Your message is ready.');
        return;
      }
      var submit = form.querySelector('button[type="submit"]');
      submit.disabled = true;
      submit.textContent = 'Sending…';
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(d),
      }).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        result.hidden = false;
        result.innerHTML = '';
        var ok = document.createElement('p');
        ok.className = 'small';
        ok.textContent = 'Thanks, ' + d.name + '. We have your message and an engineer will reply, usually within one business day.';
        result.appendChild(ok);
        result.focus();
        form.reset();
      }).catch(function () {
        showFallback(d, 'We could not send the form just now, but your message is saved below.');
      }).then(function () {
        submit.disabled = false;
        submit.textContent = 'Send message';
      });
    });
  }
})();
