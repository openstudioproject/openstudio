import React, { Component } from "react"
import PageTemplate from "../../components/PageTemplate"
import { intlShape } from "react-intl"

// add proptypes

class homeComponent extends Component {
    constructor(props) {
        super(props)
    }

    PropTypes = {
        intl: intlShape.isRequired
    }

    // componentWillMount() {
    //     this.props.setLoading(true)
    // }

    componentDidMount() {
        setTimeout(() => this.props.setLoadingMessage('phase 1'), 500)
        setTimeout(() => this.props.setLoadingMessage('phase 2'), 1500)
        setTimeout(() => this.props.setLoadingMessage('phase 3'), 2500)
        // ready...
        setTimeout(() => this.props.setLoading(false), 3000)
        setTimeout(() => this.props.setLoadingMessage('Loading done!'), 3500)
        
    }

    render() {
        return (
            <PageTemplate app_state={this.props.app_state}>
            <section className="Welcome">
                <div>Welcome page</div>
                <div>{this.props.app_state.loading}</div>
                <div>{this.props.app_state.loading_message}</div>
                {this.props.intl.formatMessage({ id: 'app.pos.home.hello' })}
            </section>
            </PageTemplate>
        )
    }
}

export default homeComponent
