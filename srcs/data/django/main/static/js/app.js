currentPage = '';

document.addEventListener("DOMContentLoaded", function() {

  // 3分ごとにheartbeatを送信
  setInterval(sendHeartbeat, 3 * 60 * 1000);
  // ページ読み込み時に初回heartbeatを送信
  sendHeartbeat();

  var postData = {};
  postData['page'] = 'top'; 
  postData['data_url']= 'process-post/';
  send_ajax(postData);

  // CSRFトークンをmetaタグから取得
  var csrfToken = getCSRFToken();
  
  // var links = document.querySelectorAll(".post-link");
  // links.forEach(function(link) {
  //   link.addEventListener("click", function(event) {
  //     event.preventDefault();
  // // 属性を取得し、オブジェクトに変換
  //     var postData = {};
  //     Array.from(link.attributes).forEach(function(attr) {
  //       postData[attr.name] = attr.value;
  //     });


  //     send_ajax(postData);
  //   });
  // });

  // イベントデリゲーションを使用してaタグのクリックイベントを処理
  document.addEventListener('click', function(event) {
    var link = event.target;
    // 子要素がクリックされた場合も考慮
    while (link && link.tagName !== 'A') {
      link = link.parentElement;
    }
    if (link != null && link.tagName === 'A') {
      event.preventDefault();
      // 属性を取得し、オブジェクトに変換
      var postData = {};
      Array.from(link.attributes).forEach(function(attr) {
        postData[attr.name] = attr.value;
      });
      var classes = postData['class'] ? postData['class'].split(' ') : [];
      if (classes.includes('post-link')) {
        send_ajax(postData);
      }
    }
  });

  document.addEventListener('submit', function(event) {
    //ファイルをアップロードするときのform
    if (event.target.matches('.ajax-upload'))
    {
        event.preventDefault();

        var image = document.getElementById('image').files[0];

        var maxSize = 5 * 1024 * 1024;  // 5MB
        if (image.size > maxSize) {
            document.getElementById('result').innerText = "ファイルサイズが5MBを超えています。";
            return;
        }

        var formData = new FormData();
        formData.append('image', image);
        formData.append('imgtagid', 'uploaded');
        formData.append('msgtagid', 'result');

        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'upload/', true);

        xhr.onload = function() {
            if (xhr.status === 200) {
              const response = JSON.parse(xhr.responseText);
              lang = getCookie('language') || 'ja';
              if (lang === 'ja') {
                document.getElementById('result').innerHTML = "<div class=\"translations\" id=\"upload\">アップロードが成功しました\nこの画像を保存しますか？</div>";
              } else if (lang === 'en') {
                document.getElementById('result').innerHTML = "<div class=\"translations\" id=\"upload\">Upload succeeded\nWould you like to save this image?</div>";
              } else {
                document.getElementById('result').innerHTML = "<div class=\"translations\" id=\"upload\">업로드가 성공했습니다\n이 이미지를 저장하시겠습니까?</div>";
              }
              document.getElementById('uploaded').src = response.imgsrc;
              document.getElementById('descimage').innertext ="画像";
              if (typeof response.setid !== 'undefined') {     
                setIdValue(response.setid, response.setvalue);
              }
            } else {
                document.getElementById('result').innerText = JSON.parse(xhr.responseText).error;
            }
            gameSocket.close();
          };
        xhr.send(formData);

    //textデータを送信するときのform
    } else if (event.target.matches('.ajax-form')) {
      event.preventDefault();
      
      const form = event.target;
      const formData = new FormData(form);
      const formJSON = Object.fromEntries(formData.entries());


      const xhr = new XMLHttpRequest();
      xhr.open('POST', form.action, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
  
      csrfToken = getCSRFToken();
      // CSRFトークンの変数が未定義でないことを確認
      if (typeof csrfToken !== 'undefined') {
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
      } else {
        console.error('CSRF token is not defined.');
        return;
      }
  
      xhr.onload = function() {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          // データを更新する
          updateContent(response);
          // 履歴にページを登録
          history.pushState({ data: response }, response.title, '');
        } else {
          console.error('Error:', xhr.statusText);
            // エラー処理をここに追加します     
        }
        loadLanguage();
        gameSocket.close();

      };
  
      xhr.onerror = function() {
        console.error('Request failed');
        // ネットワークエラーの処理をここに追加します
      };

      xhr.send(JSON.stringify(formJSON));
    }
  });
});

// popstateイベントをリッスン
window.addEventListener("popstate", function(event) {
  if (event.state) {
    // 状態オブジェクトが存在する場合、表示内容を更新
    updateContent(event.state.data);


  }
});
  
function updateContent(data) {
  // 表示内容をデータに基づいて更新する処理
  // ここに実際の更新ロジックを記述

  //本来は失敗したときのことを記述したりすべき
  updateCSRFToken()

  currentPage = data.page;

  // ページのコンテンツを更新
  if (typeof data.content !== 'undefined') {     
    document.querySelector('#content').innerHTML = data.content;
  }
  if (typeof data.head !== 'undefined') {     
    document.querySelector('#head').innerHTML = data.head;
  }
  if (typeof data.foot !== 'undefined') {     
    document.querySelector('#foot').innerHTML = data.foot;
  }
  // if (typeof data.exec !== 'undefined') {     
  //   eval(data.exec);
  // }
  if (typeof data.alert !== 'undefined') {     
    popupAlert(data.alert);
  }
  if (typeof data.setid !== 'undefined') {     
    setIdValue(data.setid, data.setvalue);
  }
  if (typeof data.reload !== 'undefined') {
    reloadAjax(data.reload, data.timeout);
  }
  if (typeof data.login !== 'undefined') {
    
    console.log(data.login)
    console.log(data.elem)
    toggleVisibility(data.login, data.username, data.elem)
  }
  if (typeof data.isValid !== 'undefined') {
    console.log('defined')
    displayAlert(data.elem)
  }
  if (typeof data.title !== 'undefined') {     
    document.title = data.title;
  } else {
    document.title = '42tokyo';
  }



  if (typeof data.rawscripts !== 'undefined') {     
    //ここからheaderにscriptをいれる <data.rawscripts> 
    jsCode = data.rawscripts;
    // <head> タグを取得
    const head = document.head;
    // 既存のスクリプトタグを削除
    const scripts = head.querySelectorAll('script');
    scripts.forEach(script => script.remove());
    // 新しいスクリプトタグを作成してコードを追加
    const jsScript = document.createElement('script');
    jsScript.textContent = jsCode;
    // <head> タグに新しいスクリプトタグを挿入
    head.appendChild(jsScript);
  }

  //ここからfootにscriptfileをいれる <data.scriptfiles>
  if (typeof data.scriptfiles !== 'undefined') {     
    jsFiles = data.scriptfiles;
    scriptFiles = jsFiles.trim().split("\n");
    for (i = 0; i < scriptFiles.length; i++) {
      //値が空のときは実行しない
      if (scriptFiles[i] === "")
        continue;
      // 新しいスクリプトタグを作成してコードを追加
      let arrayScript = document.createElement('script');
      //キャッシュされたjsファイルが利用されないようにtimestampを付加する
      // arrayScript.src = scriptFiles[i].trim() + "?ts=" + new Date().getTime();
      arrayScript.src = scriptFiles[i].trim();
      // <foot> タグに新しいスクリプトタグを挿入
      foot.appendChild(arrayScript);
    }


  }


  loadLanguage();
  
  // var links = document.getElementById('content').querySelectorAll(".post-link");  
  // links.forEach(function(link) {
  //   link.addEventListener("click", function(event) {
  //     event.preventDefault();
  // // 属性を取得し、オブジェクトに変換
  //     var postData = {};
  //     Array.from(link.attributes).forEach(function(attr) {
  //       postData[attr.name] = attr.value;
  //     });
  //     send_ajax(postData);
  //   });
  // });
}



function sendHeartbeat() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'heartbeat/', true);
  xhr.withCredentials = true;

  xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
          if (xhr.status === 200) {
              var response = JSON.parse(xhr.responseText);
              console.log('User is:', response.status);
              // ログイン状態に応じた処理
          } else {
              console.error('Error: ', xhr.status);
              // ログアウト状態に応じた処理
          }
      }
  };

  xhr.send();
}

function send_ajax(data)
{
  // CSRFトークンをmetaタグから取得
  const csrfToken = getCSRFToken();

  var xhr = new XMLHttpRequest();
  xhr.open("POST", data.data_url, true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("X-CSRFToken", csrfToken);  // CSRFトークンをヘッダーに設定
  xhr.onreadystatechange = function() {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      var parser = new DOMParser();
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        //データを更新する
        updateContent(response);
        loadLanguage();
        //履歴にページを登録
        history.pushState({ data: response }, response.title, '');
      } else {
        console.error('There was a problem with the request:', xhr.statusText);
      }
    }
  };  
  xhr.send(JSON.stringify(data));
}

// CSRFトークンを取得する関数
function getCSRFToken() {
  return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// CSRFトークンを更新する関数
function updateCSRFToken(callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'get-csrf-token/', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
          var data = JSON.parse(xhr.responseText);
          document.querySelector('meta[name="csrf-token"]').setAttribute('content', data.csrfToken);
          if (callback) callback();
      }
  };
  xhr.send();
}

function sendHeartbeat() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'heartbeat/', true);
  xhr.withCredentials = true;

  xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
          if (xhr.status === 200) {
              var response = JSON.parse(xhr.responseText);
              console.log('User is:', response.status);
              // ログイン状態に応じた処理
          } else {
              console.error('Error: ', xhr.status);
              // ログアウト状態に応じた処理
          }
      }
  };

  xhr.send();
}

function reloadAjax(page, timeout) {
  setTimeout(() => {
    if (currentPage == page)
      {
        var postData = {};
        postData['page'] = page; 
        postData['data_url']= 'process-post/';
        send_ajax(postData);
      } 
  }, timeout)
}

function popupAlert(mesg) {
  alertBox = document.getElementById('custom-alert');
  lang = getCookie('language') || 'ja';
  if (lang === 'ja') {
    alertBox.innerText = mesg;
  } else if (lang === 'en') {
    if (mesg === 'ログアウトしました') {
      alertBox.innerText = 'Logged out'
    } else if (mesg === 'サインアップしました') {
      alertBox.innerText = 'Signed up'
    } else if (mesg === 'ログインしました') {
      alertBox.innerText = 'Logged in'
    } else if (mesg === '追加しました') {
      alertBox.innerText = 'Added'
    } else if (mesg === '承認しました') {
      alertBox.innerText = 'Accepted'
    } else if (mesg === '対戦相手を待っています') {
      alertBox.innerText = 'Waiting for a player'
    } else if (mesg === '参加者を待っています') {
      alertBox.innerText = 'Waiting for players'
    }
  } else {
    if (mesg === 'ログアウトしました') {
      alertBox.innerText = 'L로그아웃했습니다'
    } else if (mesg === 'サインアップしました') {
      alertBox.innerText = '사인업했습니다'
    } else if (mesg === 'ログインしました') {
      alertBox.innerText = '로그인했습니다'
    } else if (mesg === '追加しました') {
      alertBox.innerText = '추가했습니다'
    } else if (mesg === '承認しました') {
      alertBox.innerText = '승인했습니다'
    } else if (mesg === '対戦相手を待っています') {
      alertBox.innerText = '대전 상대를 기다리고 있습니다'
    } else if (mesg === '参加者を待っています') {
      alertBox.innerText = '참가자를 기다리고 있습니다'
    }
  }
  alertBox.style.display = 'block';
  setTimeout(() => {
      alertBox.style.display = 'none';
  }, 2000);
}


function setIdValue(id, setvalue) {
  document.getElementById(id).value = setvalue;
}

function toggleVisibility(login, username, elem) {
  const nav = document.getElementById('navbarCollapse');
  nav.innerHTML = '';
  console.log(elem)
  if (login === 'false') {
    nav.innerHTML = `
      <ul class="navbar-nav ms-auto" id="navbar_before_login">
        <li class="nav-item">
            <a href="#" class="nav-link active post-link translations" aria-current="page" data_url="process-post/" page="signup" title="signup" id="navbar_signup">　</a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link active post-link translations" aria-current="page" data_url="process-post/" page="login" title="login" id="navbar_login">　</a>
        </li>
      </ul>
      <ul class="navbar-nav ms-auto">
          <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle translations" href="#" id="languageDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">　</a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="languageDropdown">
                  <li><a class="dropdown-item" href="#" onclick="setLanguage('ja')">日本語</a></li>
                  <li><a class="dropdown-item" href="#" onclick="setLanguage('en')">English</a></li>
                  <li><a class="dropdown-item" href="#" onclick="setLanguage('kr')">한국어</a></li>
              </ul>
          </li>
      </ul>
    `;
  } else {
    nav.innerHTML = `
      <ul class="navbar-nav mx-auto">
        <li class="nav-item">
          <a href="#" class="nav-link active post-link" aria-current="page" data_url="process-post/" page="lobby" title="lobby">Pong Lobby</a>
        </li>
      </ul>
      <ul class="navbar-nav">
        <li class="nav-item">
          <a href="#" class="nav-link active post-link" data_url="process-post/" page="ponggame" title="Pong Game">Ponggame</a>
        </li>
      </ul>
      <ul class="navbar-nav">
        <li class="nav-item">
          <a href="#" class="nav-link active post-link" data_url="process-post/" page="gamelist2" title="Game List 2">GameList2</a>
        </li>
      </ul>


      <ul class="navbar-nav ms-auto">
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              ${username}
            </a>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
              <li><a class="dropdown-item post-link translations" href="#" data_url="process-post/" page="profile" title="Profile" id="navbar_profile">　</a></li>
              <li><a class="dropdown-item post-link translations" href="#" data_url="process-post/" page="friends" title="Friends" id="navbar_friends">　</a></li>
              <li><a class="dropdown-item post-link translations" href="#" data_url="process-post/" page="logout" title="Logout" id="navbar_logout">　</a></li>
            </ul>
        </li>
      </ul>
      <ul class="navbar-nav ms-auto">
          <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle translations" href="#" id="languageDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">　</a>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="languageDropdown">
                  <li><a class="dropdown-item" href="#" onclick="setLanguage('ja')">日本語</a></li>
                  <li><a class="dropdown-item" href="#" onclick="setLanguage('en')">English</a></li>
                  <li><a class="dropdown-item" href="#" onclick="setLanguage('kr')">한국어</a></li>
              </ul>
          </li>
      </ul>
    `;
  }
  if (elem === 'top') {
    const top = document.getElementById('expranations');
    top.innerHTML = '';
    if (login === 'false') {
      top.innerHTML = `
        <div class="translations mb-2" id="top1_l1">　</div>
        <div class="translations mb-2" id="top1_l2">　</div>
        <div class="translations mb-2" id="top1_l3">　</div>
        <div class="translations mb-2" id="top1_l4">　</div>
        <div class="translations mb-5" id="top1_l5">　</div>
      `;
    } else {
      top.innerHTML = `
        <div class="translations mb-2" id="top2_l1">　</div>
        <div class="translations mb-2" id="top2_l2">　</div>
        <div class="translations mb-2" id="top2_l3">　</div>
        <div class="translations mb-5" id="top2_l4">　</div>
    `;
    }
  }
  loadLanguage();
}

function displayAlert(elem) {
  // console.log(elem);
  lang = getCookie('language') || 'ja';
  if (elem === 'room') {
    const alert = document.getElementById('roomAlertBlock');
    alert.innerHTML = '';
    if (lang === 'ja') {
      alert.innerHTML = `
        <div id="room_warning" class="card-text text-warning translations">そのルームには入れません</div>
      `;
    } else if (lang === 'en') {
      alert.innerHTML = `
        <div id="room_warning" class="card-text text-warning translations">You cannot enter the room</div>
      `;
    } else {
      alert.innerHTML = `
        <div id="room_warning" class="card-text text-warning translations">그 룸에는 들어갈 수 없습니다</div>
      `;
    }
  } else if (elem === 'tournament') {
    const alert = document.getElementById('tournamentAlertBlock');
    alert.innerHTML = '';
    if (lang === 'ja') {
      alert.innerHTML = `
        <div id="tournament_warning" class="card-text text-warning translations">そのトーナメントには参加できません</div>
      `;
    } else if (lang === 'en') {
      alert.innerHTML = `
        <div id="tournament_warning" class="card-text text-warning translations">You cannot join the tournament</div>
      `;
    } else {
      alert.innerHTML = `
        <div id="tournament_warning" class="card-text text-warning translations">그 토너먼트에는 참가할 수 없습니다</div>
      `;
    }
  }
}

function setCookie(name, value, days) {
  var expires = "";
  if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

function applyTranslations(translations) {
  var elements = document.querySelectorAll('.translations');
  elements.forEach(function (element) {
      var translationKey = element.id;
      if (translations[translationKey]) {
          element.textContent = translations[translationKey];
          console.log(element.textContent)
      } 
  });
}

function setLanguage(lang) {
  setCookie('language', lang, 7); // 言語設定を7日間保存

  // console.log(lang)
  
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/static/translations/' + lang + '.json', true);

  xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {
          var translations = JSON.parse(xhr.responseText);
          applyTranslations(translations);
      } else if (xhr.readyState === 4) {
          // console.error('Error loading translations:', xhr.statusText);
      }
  };

  xhr.send();
}

function loadLanguage() {
  lang = getCookie('language') || 'ja'; // クッキーが見つからない場合はデフォルトで'ja'を使用
  setLanguage(lang);
}

// ページが読み込まれた時に言語を読み込む
window.onload = loadLanguage;

