$(function() {
  $('.js-pagetop').hide();

  $(window).on('scroll', function () {
    if ($(this).scrollTop() > 100) {
      $('.js-pagetop').fadeIn('fast');
    } else {
      $('.js-pagetop').fadeOut('fast');
    }

    var scrollHeight = $(document).height();
    var scrollPosition = $(window).height() + $(window).scrollTop();
    var footHeight = $('.footer').innerHeight();
    if (scrollHeight - scrollPosition <= footHeight) {
      $('.js-pagetop').css({ position: 'absolute', bottom: footHeight + 40 });
    } else {
      $('.js-pagetop').css({ position: 'fixed', bottom: '40px' });
    }
  });

  $('.js-pagetop').on('click', function () {
    $('body,html').animate({ scrollTop: 0 }, 400);
    return false;
  });

  // ページ読み込み時の位置調整(固定ヘッダー分のオフセット補正)
  var hash = location.hash;
  if ($(hash).length) {
    var pos = $(hash).offset().top - $('.header').innerHeight();
    setTimeout(function () {
      $('html, body').scrollTop(pos - 50);
    }, 10);
  }
});
