<head>
  <script>
    function togglePersistency(id) {
      // send sql statement
      alert('toggling persistency for ' + id)
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
        <tr>
        %for col in rule:
            <td onclick="handleClick('{{col.id}}');">{{col}}</td>
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
