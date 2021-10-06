(function (fsadmin) {
    function tinymceFilePickerCallback (pickerCallback, value, meta) {
      var win = window.tinymce.activeEditor.windowManager.open({
        url: fsadmin.TINYMCE_DIALOG_URL,
        width: 600,
        height: 400,
        title: 'Choose file'
      }, {
  
      });
  
      win.$el.find('iframe').on('load', function () {
        var subWindow = win.$el.find('iframe')[0].contentWindow;
        var links = subWindow.document.querySelectorAll('a.item.file')
        for (var i = 0; i < links.length; i++) {
          links[0].addEventListener('click', function () {
            pickerCallback(this.getAttribute('href'));
            win.close();
            return false;
          });
        }
  
        // subWindow.$('a.item.file').on('click', function () {
        //   pickerCallback(this.getAttribute('href'));
        //   win.close();
        //   return false;
        // });
      });
  
      // // Provide file and text for the link dialog
      // if (meta.filetype == 'file') {
      //   callback('mypage.html', {text: 'My text'});
      // }
      //
      // // Provide image and alt text for the image dialog
      // if (meta.filetype == 'image') {
      //   callback('myimage.jpg', {alt: 'My alt text'});
      // }
      //
      // // Provide alternative source and posted for the media dialog
      // if (meta.filetype == 'media') {
      //   callback('movie.mp4', {source2: 'alt.ogg', poster: 'image.jpg'});
      // }
    }
  
    fsadmin.tinymceFilePickerCallback = tinymceFilePickerCallback;
  })(window.fsadmin);
  