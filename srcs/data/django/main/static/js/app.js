// ルーティング
const routes = {
    '/': () => {
      // トップページを表示
      document.getElementById('app').innerHTML = '<h1>Top Page</h1>';
    },
    '/about': () => {
        // アバウトページを表示
        document.getElementById('app').innerHTML = '<h1>About Page</h1>';
    },
    '/second': () => {
        // アバウトページを表示
        document.getElementById('app').innerHTML = '<h1>second Page</h1>';
    },
};
  
  // パスに一致するルートを検索して実行
  const navigateTo = (path) => {
    const route = routes[path] || routes['/'];
    route();
  };
  
  // 初期ページ
  // 初期ページの表示
navigateTo(window.location.pathname);

// ハッシュ変更イベントのハンドリング
window.addEventListener('hashchange', () => {
  navigateTo(window.location.hash.slice(1));
});

