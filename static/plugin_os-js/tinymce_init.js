//TODO: add different profiles which can be triggerec by different classes eg. tmce-basic tmce-advanced tmce-etc..

function tinymce_init_default() {
    tinymce.init({
      selector: 'textarea.tmced',
      height: 200,
      plugins: [
        'advlist autolink lists link image charmap print preview anchor',
        'searchreplace visualblocks hr code fullscreen',
        'insertdatetime textcolor media table contextmenu paste'
      ],
      menubar: false,
      toolbar: 'bold italic underline forecolor | bullist numlist | alignleft aligncenter alignright | link unlink image table | code | pastetext',
      setup : function(editor) {
        editor.on('init', function() {
            this.getDoc().body.style.fontSize = '13px';
        });
        editor.on('change', function () {
            editor.save();
        });
      }
  });
}

tinymce_init_default();
