import { connect } from 'react-redux'

const mapStateToProps = state => 
    ({
        settings: state.app.settings.data
    })

// const mapDispatchToProps = dispatch =>
//     ({
//        setPageTitle(title) {
//            dispatch(appOperations.setPageTitle(title))
//        }
//     })

import React from "react"

const Currency = ({settings, amount}) =>
    <span>
        {settings.currency_symbol} { ' ' }
        {amount.toFixed(2)}
    </span>

// const SubscriptionsContainer = withRouter(injectIntl(connect(
//     mapStateToProps,
//     mapDispatchToProps
// )(Subscriptions)))

// export default SubscriptionsContainer


const ConnectedCurrency = connect(
    mapStateToProps
)(Currency)

export default ConnectedCurrency