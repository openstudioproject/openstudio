import React, { Component } from "react"

class ButtonVerify extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchRevenue: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        attendance: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )

        this.props.fetchRevenue(this.props.match.params.clsID)
    }
    
    render() {
        return (
class Revenue extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchRevenue: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        attendance: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )

        this.props.fetchRevenue(this.props.match.params.clsID)
    }
    
    render() {
        let disabled
        (teacher_payment.status === 'error') ?
            disabled = "disabled" : disabled = ''

        return (
            
    
            <button  className="btn bg-olive btn-flat btn-block">
                <b>{intl.formatMessage({ id:"app.general.strings.verify" })}</b>
            </button>
        )
    }
}

export default Revenue

        )
    }
}

export default Revenue


const ButtonVerify = ({intl, teacher_payment}) => 



export default ButtonVerify