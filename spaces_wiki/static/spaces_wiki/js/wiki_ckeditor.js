// set textareas ckeditor should attach to
CKEDITOR.replaceClass='CKEditor';

var activateMarkdown = function() {
    CKEDITOR.instances[contentSelector].setMode('markdown')
};

var activateWysiwyg = function() {
    CKEDITOR.instances[contentSelector].setMode('wysiwyg')
};

var contentSelector = 'id_content'

/*
	CKEditor expects html as input, so we frontrun it a bit
	by converting the textarea markdown content first
*/
var initialMarkdown = $('#'+contentSelector).html()
$.getScript(CKEDITOR.basePath + 'plugins/markdown/js/marked.js', function() {
	$('#'+contentSelector).html(marked(initialMarkdown, {langPrefix: 'language-'}));
});

/*
  The CKEditor plugin lazyloads the markdown converter on demand.
  We explicitly load all scripts now to ensure markdown conversion is
  complete on page save.
*/
CKEDITOR.on('instanceCreated', function() {
	CKEDITOR.scriptLoader.load(CKEDITOR.basePath + 'plugins/markdown/js/to-markdown.js')
	CKEDITOR.document.appendStyleSheet(CKEDITOR.basePath + 'plugins/markdown/css/codemirror.min.css');
	CKEDITOR.scriptLoader.load(CKEDITOR.basePath + 'plugins/markdown/js/codemirror-gfm-min.js')
});


// edit article
if ($('#article_edit_form').length) {

	var formSelector = 'article_edit_form';
	var modalSelector = 'previewModal';

	var submitArticle = function(buttonSelector, target) {
		activateMarkdown();
		document.getElementById(formSelector).target=target; 
        var action = $(buttonSelector).attr('data-action')
        console.log(action)
        document.getElementById(formSelector).action=action; 
        $('#'+formSelector).submit()
	};

	// trigger markdown conversion on preview
	$('#previewButton').on('click', function(ev) {
		submitArticle('#previewButton', 'previewWindow');
		$('#'+modalSelector).modal('show'); 
	});

	// main save button
	$('#saveButton').on('click', function(ev) {
		submitArticle('#saveButton', '');
	});

	// modal save button
	$('#modalSaveButton').on('click', function(ev) {
		submitArticle('#modalSaveButton', '');
    });

	// preview close button
	$('#modalCloseButton').on('click', function(ev) {
		activateWysiwyg();
	});

}

// create article
if($('#createForm').length) {
	var formSelector = 'createForm';
	var saveButtonSelector = '#'+formSelector+' button[type="submit"]'
	$(saveButtonSelector).on('click', function(ev) {
		activateMarkdown();
	});
}