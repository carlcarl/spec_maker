/*jslint browser:true */
/*jslint es5: true */
/*jslint nomen: true */
/*global $, jQuery, alert, console, log, FormData, _*/


$(function () {
	'use strict';
	var App, $document,
		UploadProgressBarStore, UploadImageBoxStore,
		UploadProgressBarView, UploadImageBoxView;

	$document = $(document);

	UploadProgressBarView = {
		init: function ($element) {
			this.$element = $element;
			this.listener = this.handleEvent.bind(this);
			$document.on('render_progress_bar', this.listener);
		},
		handleEvent: function (evt, percent) {
			switch (evt.type) {
			case 'render_progress_bar':
				if (typeof percent === 'number') {
					percent = String(percent);
				}
				this.$element
					.css('width', percent + '%')
					.attr('aria-valuenow', percent)
					.text(percent + '%');
				break;
			}
		}

	};

	UploadProgressBarStore = {
		percent: 0,
		setPercent: function (percent) {
			this.percent = percent;
			$(document).trigger('render_progress_bar', [percent]);
		},
		getPercent: function () {
			return this.percent;
		},
	};

	UploadImageBoxView = {
		init: function ($element) {
			this.$element = $element;
			this.listener = this.handleEvent.bind(this);
			$document.on('render_upload_image_box', this.listener);
		},
		handleEvent: function (evt, ifShowBorder) {
			switch (evt.type) {
			case 'render_upload_image_box':
				console.log(evt);
				this.$element.toggleClass('border', ifShowBorder);
				break;
			}
		},
	};

	UploadImageBoxStore = {
		ifShowBorder: false,
		addBorder: function () {
			this.ifShowBorder = true;
			$document.trigger('render_upload_image_box', [this.ifShowBorder]);
		},
		removeBorder: function () {
			this.ifShowBorder = false;
			$document.trigger('render_upload_image_box', [this.ifShowBorder]);
		},
		handleFileUpload: function (files) {
			var i, len, formData, imagesType;
			imagesType = {
				'image/jpeg': true,
				'image/jpg': true,
				'image/png': true,
				'image/gif': true,
				'image/bmp': true
			};
			
			for (i = 0, len = files.length; i < len; i += 1) {
				if (imagesType[files[i].type]) {
					formData = new FormData();
					formData.append('file', files[i]);

					this.sendFileToServer(formData);
				} else {
					this.addMessage(
						'alert-danger',
						imagesType[files[i].type] + ': Unsupported file type'
					);
				}
			}
		},
		addMessage: function (alertClass, message) {
			var messageTemplate;
			messageTemplate = _.template(
				$('#message-template').html(),
				{
					'alertClass': alertClass,
					'message': message
				}
			);
			$('#message-box').prepend(messageTemplate);
		},
		sendFileToServer: function (formData) {
			var uploadURL, self;
			self = this;
			uploadURL = "/upload_image/"; //Upload URL
			// ref: http://hayageek.com/drag-and-drop-file-upload-jquery/
			$.ajax({
				xhr: function () {
					var xhrobj, percent, position, total;
					xhrobj = $.ajaxSettings.xhr();
					if (xhrobj.upload) {
						xhrobj.upload.addEventListener('progress', function (event) {
							percent = 0;
							position = event.loaded || event.position;
							total = event.total;
							if (event.lengthComputable) {
								percent = Math.ceil(position / total * 100);
							}
							UploadProgressBarStore.setPercent(percent);
						}, false);
					}
					return xhrobj;
				},
				url: uploadURL,
				type: "POST",
				contentType: false,
				processData: false,
				cache: false,
				data: formData,
				success: function (data) {
					console.log(data);
					UploadProgressBarStore.setPercent(100);
					// this.$uploadImageBox.css('border', 'none');
					if (data.error === 'undefined') {
						alert('Response format is wrong!');
						return;
					}
					if (data.error === 0) {
						self.addMessage('alert-success', data.message);
					} else {
						self.addMessage('alert-danger', data.message);
					}
					//$("#status1").append("File upload Done<br>");           
				}
			});
		},
	};

	App = {
		init: function () {
			this.$uploadImageBox = $("#upload-image-box");
			this.$uploadProgressBar = $('#upload-progress-bar');
			UploadProgressBarView.init(this.$uploadProgressBar);
			UploadImageBoxView.init(this.$uploadImageBox);

			this.listener = this.handleEvent.bind(this);
			this.$uploadImageBox
				.on('dragenter', this.listener)
				.on('dragover', this.listener)
				.on('drop', this.listener);

			$document.on('dragenter', function (e) {
				e.stopPropagation();
				e.preventDefault();
			}).on('dragover', function (e) {
				e.stopPropagation();
				e.preventDefault();
				UploadImageBoxStore.addBorder();
			}).on('drop', function (e) {
				e.stopPropagation();
				e.preventDefault();
			});

		},
		handleEvent: function (evt) {
			switch (evt.type) {
			case 'dragenter':
				evt.stopPropagation();
				evt.preventDefault();
				UploadImageBoxStore.addBorder();
				break;
			case 'dragover':
				evt.stopPropagation();
				evt.preventDefault();
				break;
			case 'drop':
				console.log('drop!');
				evt.preventDefault();
				UploadImageBoxStore.removeBorder();
				UploadProgressBarStore.setPercent(0);
				var files = evt.originalEvent.dataTransfer.files;
				//We need to send dropped files to Server
				UploadImageBoxStore.handleFileUpload(files);
				break;
			}

		},
	};
	App.init();
/*
	var $uploadImageBox, $uploadProgressBar;

	function setProgress(percent) {
		if (typeof percent === 'number') {
			percent = String(percent);
		}
		$uploadProgressBar
			.css('width', percent + '%')
			.attr('aria-valuenow', percent)
			.text(percent + '%');
	}

	function addMessage(alertClass, message) {
		var messageTemplate;
		messageTemplate = _.template(
			$('#message-template').html(),
			{
				'alertClass': alertClass,
				'message': message
			}
		);
		$('#message-box').prepend(messageTemplate);
	}

	function sendFileToServer(formData) {
		var uploadURL;
		uploadURL = "/upload_image/"; //Upload URL
		$.ajax({
			xhr: function () {
				var xhrobj, percent, position, total;
				xhrobj = $.ajaxSettings.xhr();
				if (xhrobj.upload) {
					xhrobj.upload.addEventListener('progress', function (event) {
						percent = 0;
						position = event.loaded || event.position;
						total = event.total;
						if (event.lengthComputable) {
							percent = Math.ceil(position / total * 100);
						}
						setProgress(percent);
					}, false);
				}
				return xhrobj;
			},
			url: uploadURL,
			type: "POST",
			contentType: false,
			processData: false,
			cache: false,
			data: formData,
			success: function (data) {
				console.log(data);
				setProgress(100);
				$uploadImageBox.css('border', 'none');
				if (data.error !== 'undefined') {
					if (data.error === 0) {
						addMessage('alert-success', data.message);
					} else {
						addMessage('alert-danger', data.message);
					}
				} else {
					alert('Response format is wrong!');
				}
				//$("#status1").append("File upload Done<br>");           
			}
		});
		// status.setAbort(jqXHR);
	}

	function handleFileUpload(files) {
		var i, len, formData, imagesType, messageTemplate;
		imagesType = {
			'image/jpeg': true,
			'image/jpg': true,
			'image/png': true,
			'image/gif': true,
			'image/bmp': true
		};
		
		for (i = 0, len = files.length; i < len; i += 1) {
			if (imagesType[files[i].type]) {
				formData = new FormData();
				formData.append('file', files[i]);

				sendFileToServer(formData);
			} else {
				messageTemplate = _.template(
					$('#message-template').html(),
					{
						'alertClass': 'alert-danger',
						'message': 'Unsupported file type'
					}
				);
				$('#message-box').prepend(messageTemplate);
			}
		}
	}

	$uploadProgressBar = $('#upload-progress-bar');
	$uploadImageBox = $("#upload-image-box");
	$uploadImageBox.on('dragenter', function (e) {
		e.stopPropagation();
		e.preventDefault();
		$(this).css('border', '2px solid #0B85A1');
	}).on('dragover', function (e) {
		e.stopPropagation();
		e.preventDefault();
	}).on('drop', function (e) {
		console.log('drop!');
		$(this).css('border', 'none');
		e.preventDefault();
		var files = e.originalEvent.dataTransfer.files;
		setProgress(0);
		//We need to send dropped files to Server
		handleFileUpload(files);
	});


	$(document).on('dragenter', function (e) {
		e.stopPropagation();
		e.preventDefault();
	}).on('dragover', function (e) {
		e.stopPropagation();
		e.preventDefault();
		$uploadImageBox.css('border', '2px dotted #0B85A1');
	}).on('drop', function (e) {
		e.stopPropagation();
		e.preventDefault();
	});
	*/


});
// vim: set tabstop=4 noexpandtab shiftwidth=4 softtabstop=4:
