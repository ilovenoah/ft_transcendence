document.addEventListener("DOMContentLoaded", function() {
    var links = document.querySelectorAll(".post-link");
  
    // CSRFトークンをmetaタグから取得
    var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  
    links.forEach(function(link) {
        link.addEventListener("click", function(event) {
            event.preventDefault();
  
       // 属性を取得し、オブジェクトに変換
        var postData = {};
        Array.from(link.attributes).forEach(function(attr) {
            postData[attr.name] = attr.value;
        });

        var xhr = new XMLHttpRequest();
        xhr.open("POST", link.getAttribute("data-url"), true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.setRequestHeader("X-CSRFToken", csrfToken);  // CSRFトークンをヘッダーに設定
  
        xhr.onreadystatechange = function() {
          if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
              var response = JSON.parse(xhr.responseText);
              console.log(response);
            } else {
              console.error('There was a problem with the request:', xhr.statusText);
            }
          }
        };
  
        xhr.send(JSON.stringify(postData));
      });
    });
  });