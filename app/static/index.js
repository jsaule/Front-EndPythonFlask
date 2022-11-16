function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }

  function deleteTag(tagId) {
    fetch("/delete-tag", {
      method: "POST",
      body: JSON.stringify({ tagId: tagId }),
    }).then((_res) => {
      window.location.href = "/tags";
    });
  }