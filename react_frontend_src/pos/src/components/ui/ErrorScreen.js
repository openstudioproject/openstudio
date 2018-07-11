import React from "react"
// import '../../../stylesheets/components/ui/LoadingScreen.scss'

// function dumpObject(obj)
// {
//   var od = new Object;
//   var result = "";
//   var len = 0;

//   for (var property in obj)
//   {
//     var value = obj[property];
//     if (typeof value == 'string')
//       value = "'" + value + "'";
//     else if (typeof value == 'object')
//     {
//       if (value instanceof Array)
//       {
//         value = "[ " + value + " ]";
//       }
//       else
//       {
//         var ood = dumpObject(value);
//         value = "{ " + ood.dump + " }";
//       }
//     }
//     result += "'" + property + "' : " + value + ", ";
//     len++;
//   }
//   od.dump = result.replace(/, $/, "");
//   od.len = len;

//   return od;
// }


const ErrorScreen = ({message, data}) =>
    <div className="os_error">
        <div className="os_error_content">
            <h1>Un oh... an error has occurred </h1>
            <h2>{message}</h2>
            See the console for more information. <br /><br />
            Additional information: <br/>
            {data}
        </div>
    </div>

export default ErrorScreen