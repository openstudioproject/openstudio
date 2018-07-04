import { connect } from 'react-redux';
import { IntlProvider } from 'react-intl'


function mapStateToProps(state) {
    console.log(state)
    const {language, messages} = state.root.locale
    return {locale: language, key: language, messages}
}


export default connect(mapStateToProps)(IntlProvider)