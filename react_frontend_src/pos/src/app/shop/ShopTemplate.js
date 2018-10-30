import React from "react"
  
// add protypes

// import PosMenu from "./PosMenu"
// import Content from "./ui/Content";
// import ErrorScreen from "./ui/ErrorScreen";

import PageTemplate from '../../components/PageTemplate'
import ShopMainMenu from "./MainMenu";

const ShopTemplate = ({ app_state, children }) =>
    <PageTemplate app_state={app_state}>
        <div className="row">
            <div className="col-md-4">
            Shopping cart, select customer & cart tools
            </div>
            <div className="col-md-8">
            <ShopMainMenu>
                {children}
            </ShopMainMenu>
            </div>
        </div>
    </PageTemplate>

export default ShopTemplate



// render() {
//     return (
//         <PageTemplate app_state={this.props.app}>
//             { 
//                 (!this.props.attendance.loaded) ? 
//                     <div>Loading attendance, please wait...</div> :
//                     <section className="checkin_attendance">
//                         <div className="pull-right">
//                             <NavLink to={"/checkin/revenue/" + this.props.match.params.clsID}>
//                                 {this.props.intl.formatMessage({ id: "app.pos.checkin.attendane.verify_teacher_payment"})}
//                             </NavLink>
//                         </div>
//                         <InputGroupSearch placeholder={this.props.intl.formatMessage({ id: 'app.general.placeholders.search' })}
//                                           onChange={this.onChange.bind(this)} /> <br />
//                         <AttendanceList attendance_items={this.props.attendance.data} />
//                     </section>
//             }
//         </PageTemplate>
//     )
// }


// const PageTemplate = ({ app_state, children }) => 
//     (app_state.error) ?
//         <ErrorScreen message={app_state.error_message}
//                     data={app_state.error_data}/>:
//         <div>
//             <MainMenu />
//             <Content title={app_state.current_page_title}>
//                 {children}
//             </Content>
//             {/* <Footer /> - No footer for now, it looks cleaner and we have OpenStudio branding in the header anyway */}
//         </div>

// export default PageTemplate