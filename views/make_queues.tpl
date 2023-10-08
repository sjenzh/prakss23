<head>
  <script>
    const port=20147;
    const persistentUrl = ':${port}/toggle_persistence'
    function togglePersistency(id, persistent) {
      //TODO send sql statement
      const data = {id: id, persistency:!(Boolean(persistent))};
      fetch(persistentUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      }).then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      }).then((data) => {
      // Handle the response from the server (if needed)
      alert('Updated successfully');
    }).catch((error) => {
      console.error('There was a problem with the fetch operation:', error);
    });
}
  </script>
  <style>
  .row {
      display: flex;
    }
  .column {
      flex: 50%;
  }
  </style>
</head>
<div class="row">
  <div class="column">
    <h2><b>Rule Queue</b></h2>
    <table border="1">
    %for rule in rules:
        <tr onclick="togglePersistency({{rule[0]}},{{rule[-1]}});">
        %for col in rule:
            <td>{{col}}</td>
	    <script>
	    	console.log("Type of col: " + typeof {{col}});
	    </script>
        %end
        </tr>
    %end
    </table>
  </div>
  <div class="column">
    <h2><b>Message Queue</b></h2>
    <table border="1">
    %for message in messages:
        <tr>
        %for col in message:
            <td>{{col}}</td>
        %end
        </tr>
    %end
    </table>
  </div>
</div>
