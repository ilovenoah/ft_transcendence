// コンテンツをロードして表示
function loadContent(url) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        document.getElementById("content").innerHTML = this.responseText;
        // URLを変更せずに履歴を追加
        window.history.pushState(url, url, url);
      }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
  }
  
  // ページの初期状態を設定
  window.onload = function() {
    // URLからページをロード
    var url = window.location.pathname.split("/").pop();
    if (url === "") {
      url = "/main/first/"; // デフォルトのページ
    }
    loadContent(url);
  };
  
  // ブラウザの戻るボタンが押されたときの処理
  window.onpopstate = function(event) {
    if (event.state && event.state.page) {
      loadContent(event.state.page);
    }
  };