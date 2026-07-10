$(document).ready(function() {

  // 初回読み込み時は必ず実行(pageshowのタイミング次第で発火が間に合わず
  // 一覧が空白のままになる不具合があったため、ready時にも確実に実行する)
  function restoreAndSearch() {
    if (typeof CAST_DATA !== 'undefined') {
      restoreSearchState(); // 1. 前回のチェック状態を完全復元
      executeSearch();      // 2. その状態で自動検索を実行
    } else {
      console.error("CAST_DATA が読み込めていません。");
    }
  }
  restoreAndSearch();

  // ページがbfcacheから復元された時(戻る/進むでスクリプトが再実行されない場合)も再実行
  $(window).on('pageshow', function() {
    restoreAndSearch();
  });

  // フォーム内の項目が変わった時にリアルタイムで保存＆ソート
  $('#searchform').on('change', 'input[type="checkbox"]', function() {
    saveSearchState();
    executeSearch();
  });

  // 検索ワードが変わった時にリアルタイムで保存＆ソート
  $('#search-word').on('input', function() {
    saveSearchState();
    executeSearch();
  });

  $('#search-word').on('keypress', function(e) {
    if (e.which === 13) { 
      e.preventDefault();
      saveSearchState();
      executeSearch();
    }
  });

  // 【新機能】現在の検索条件をブラウザの短期メモリに保存する関数
  function saveSearchState() {
    const state = {
      word: $('#search-word').val(),
      sex: getCheckedValues('sex'),
      age: getCheckedValues('age'),
      cat: getCheckedValues('cat'),
      lang: getCheckedValues('lang'),
      region: getCheckedValues('region')
    };
    sessionStorage.setItem('patio_search_state', JSON.stringify(state));
  }

  // 【新機能】メモリから前回の検索条件を引っこ抜いてチェックを入れ直す関数
  function restoreSearchState() {
    const stateJson = sessionStorage.getItem('patio_search_state');
    if (!stateJson) return;
    
    try {
      const state = JSON.parse(stateJson);
      if (state.word) $('#search-word').val(state.word);
      
      restoreCheckboxes('sex', state.sex);
      restoreCheckboxes('age', state.age);
      restoreCheckboxes('cat', state.cat);
      restoreCheckboxes('lang', state.lang);
      restoreCheckboxes('region', state.region);
    } catch (e) {
      console.error("Search state restore error:", e);
    }
  }

  function restoreCheckboxes(name, values) {
    if (!values) return;
    $(`input[name="${name}[]"]`).each(function() {
      $(this).prop('checked', values.includes($(this).val()));
    });
  }

  function executeSearch() {
    const keyword = $('#search-word').val().trim().toLowerCase();
    const selectedSex = getCheckedValues('sex');
    const selectedAge = getCheckedValues('age');
    const selectedCat = getCheckedValues('cat');
    const selectedLang = getCheckedValues('lang');
    const selectedRegion = getCheckedValues('region');

    const filteredCasts = CAST_DATA.filter(cast => {
      if (keyword) {
        const nameMatch = cast.name.toLowerCase().includes(keyword);
        const careerMatch = cast.career.toLowerCase().includes(keyword);
        if (!nameMatch && !careerMatch) return false;
      }
      if (selectedSex.length > 0 && !selectedSex.includes(cast.sex)) return false;
      if (selectedAge.length > 0) {
        const ageMatch = cast.ages.some(age => selectedAge.includes(age));
        if (!ageMatch) return false;
      }
      if (selectedCat.length > 0) {
        const catMatch = cast.categories.some(cat => selectedCat.includes(cat));
        if (!catMatch) return false;
      }
      if (selectedLang.length > 0) {
        const langMatch = cast.languages.some(lang => selectedLang.includes(lang));
        if (!langMatch) return false;
      }
      if (selectedRegion.length > 0) {
        const regionMatch = cast.regions.some(reg => selectedRegion.includes(reg));
        if (!regionMatch) return false;
      }
      return true;
    });

    renderCasts(filteredCasts);
  }

  function getCheckedValues(name) {
    return $(`input[name="${name}[]"]:checked`).map(function() {
      return $(this).val();
    }).get();
  }

  function renderCasts(casts) {
    const $container = $('#cast-container');
    const $emptyMessage = $('#empty-message');
    $container.empty();

    if (casts.length === 0) {
      $emptyMessage.show();
      return;
    }

    $emptyMessage.hide();

    // 現在絞り込まれて画面に見えているキャストのID順を記憶
    const displayedIds = casts.map(cast => String(cast.id));
    sessionStorage.setItem('patio_filtered_ids', JSON.stringify(displayedIds));

    casts.forEach(cast => {
      const imgSrc = cast.image ? cast.image : 'https://patio-patio.jp/wp-content/themes/patio/img/logo.png';
      const castHtml = `
        <a href="profile/${cast.id}.html" class="profile-main__item">
          <div class="profile-main__content">
            <img src="${imgSrc}" alt="${cast.name}">
            <div class="profile-main__bottom">
              <p class="profile-main__title">${cast.name}</p>
              <p class="profile-main__career">${cast.career}</p>
            </div>
          </div>
        </a>
      `;
      $container.append(castHtml);
    });
  }
});