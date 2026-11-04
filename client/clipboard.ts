import ClipboardJS from 'clipboard';

function initClipboard() {
	const textarea = document.getElementById('id_data') as HTMLTextAreaElement;
	const pastedSuccess = document.getElementById('pasted_success');
	const copiedSuccess = document.getElementById('copied_success');
	if (!textarea || !pastedSuccess || !copiedSuccess)
		return;
	pastedSuccess.style.display = 'none';
	copiedSuccess.style.display = 'none';
	const clipboard = new ClipboardJS('#clip-btn');
	clipboard.on('success', function(e) {
		copiedSuccess.style.display = 'inline';
		setTimeout(() => copiedSuccess.style.display = 'none', 2000);
	});
	clipboard.on('error', function(e) {
		alert("Copy to clipboard failed. Please use Ctrl+C or Cmd+C to copy the text.");
	});
	textarea.addEventListener('paste', function(e) {
		pastedSuccess.style.display = 'inline';
		setTimeout(() => pastedSuccess.style.display = 'none', 2000);
	});
}

if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', initClipboard);
} else {
	initClipboard();
}
