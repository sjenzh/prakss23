$#template to generate HTML tables from a list of tuples?
<link rel="stylesheet" type="text/css" href="queues.css" />
<div class="row">
  <div class="column">
    <h2><b>Rule Queue</b></h2>
    <table border="1">
    %for rule in rules:
        <tr>
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
