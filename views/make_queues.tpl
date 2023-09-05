<style>
.row {
    display: flex;
  }
.column {
    flex: 50%;
}
</style>
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
