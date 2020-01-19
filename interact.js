var nodes = document.getElementsByClassName('node');
  for(var i = 0; i < nodes.length; i++) {
      node.onclick = function() {
          alert(this.id);
      }
  }