<!DOCTYPE html>
<html>
<head>
  <script>
    const persistentUrl = 'toggle_persistence'
    
    function togglePersistence(id, persistent) {
      const data = {"persistence":!(Boolean(persistent)), "id": id};
      const json_data = JSON.stringify(data);
      
      fetch(persistentUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: json_data,
      })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data) => {
        console.log(data)
      })
      .catch((error) => {
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
<body>
  <div class="row">
    <div class="column">
      <h2><b>Rule Queue</b></h2>
      <table border="1">
        <thead>
          <tr>
            <th scope="col">ID</th>
            <th scope="col">Sender RE</th>
            <th scope="col">Subject RE</th>
            <th scope="col">Date After</th>
            <th scope="col">Date Before</th>
            <th scope="col">Attachment Y/N</th>
            <th scope="col">Content RE</th>
            <th scope="col">Persistent</th>
          </tr>
        </thead>
        %for rule in rules:
          <tr onclick="togglePersistence({{rule[0]}},{{rule[-1]}});">
            %for col in rule:
              <td>{{col}}</td>
            %end
          </tr>
        %end
      </table>
    </div>
    <div class="column">
      <h2><b>Message Queue</b></h2>
      <table border="1">
        <thead>
          <tr>
            <th scope="col">ID</th>
            <th scope="col">Sender</th>
            <th scope="col">Subject</th>
            <th scope="col">Date</th>
            <th scope="col">Attachment</th>
            <th scope="col">Content</th>
          </tr>
        </thead>
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
</body>
</html>
