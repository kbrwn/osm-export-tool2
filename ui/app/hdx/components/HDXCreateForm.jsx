import React, { Component } from 'react';
import { Field, reduxForm } from 'redux-form';
import { connect } from 'react-redux';
import { FormGroup, ControlLabel, FormControl, HelpBlock, Row, Col, Checkbox, Panel, Button } from 'react-bootstrap';
import axios from 'axios';
import cookie from 'react-cookie';

import styles from '../styles/HDXCreateForm.css';

const form = reduxForm({
  form: 'HDXCreateForm',
  onSubmit: values => {
    console.log("Submitting form. Values:", values);
    const csrfmiddlewaretoken = cookie.load('csrftoken');

    const export_formats = [];
    ['shp','geopackage','garmin','kml','pbf'].forEach(function(f) {
      if (values[f]) {
        export_formats.push(f);
      }
    });

    const formData = {};
    Object.assign(formData,values,{'the_geom':values.aoiInfo.geojson.features[0].geometry,'export_formats':export_formats});

    axios({
        url: '/api/hdx_export_regions',
        method: 'POST',
        contentType: 'application/json; version=1.0',
        data: formData,
        headers: {"X-CSRFToken": csrfmiddlewaretoken}
    }).then((response) => {
        console.log("Success");
    }).catch((error) => {
        if (error.response) {
          console.log(error.response.data);
        }
    });
  },
});

function FieldGroup({ id, label, help, ...props }) {
  return (
    <FormGroup controlId={id}>
      <ControlLabel>{label}</ControlLabel>
      <FormControl {...props} />
      {help && <HelpBlock>{help}</HelpBlock>}
    </FormGroup>
  );
}

const renderFieldGroup = ({input, data, meta, ...props}) =>
  <FieldGroup {...input} {...props} />;

const renderTextArea = ({input, data, meta, ...props}) =>
  <FormControl componentClass='textarea' {...input} {...props} />;

const renderScheduleSelect = ({input, data, meta, ...props}) =>
  <FormControl componentClass='select' {...input} {...props}>
    <option value='day'>Daily</option>
    <option value='week'>Weekly (Sunday)</option>
    <option value='month'>Monthly (1st of month)</option>
    <option value='6hours'>Every 6 hours</option>
    <option value='never'>Don't automatically schedule</option>
  </FormControl>;

const getTimeOptions = () => {
  const options = [];

  for (let i = 0; i < 24; i++) {
    options.push(<option key={i} value={i}>{i}:00 UTC</option>);
  }

  return options;
};

const renderTimeSelect = ({input, data, meta, ...props}) =>
  <FormControl componentClass='select' {...input} {...props}>
    { getTimeOptions() }
  </FormControl>;

const renderCheckbox = ({input, data, meta, description, ...props}) =>
  <Checkbox {...input} {...props}>{description}</Checkbox>;

export class HDXCreateForm extends Component {
  componentWillReceiveProps(props) {
    props.change('aoiInfo', props.aoiInfo);
  }

  render() {
    const { handleSubmit, pristine, submitting } = this.props;

    return (
      <div className={styles.hdxCreateForm}>
        <form onSubmit={handleSubmit}>
          <h2>Create Export Region</h2>
          <Field
            id="formControlsText"
            name="dataset_prefix"
            type="text"
            label="Dataset Prefix"
            placeholder="hotosm_senegal"
            component={renderFieldGroup}
          />
          <div>Example: prefix <code>hotosm_senegal</code> results in datasets <code>hotosm_senegal_roads</code>, <code>hotosm_senegal_buildings</code>, etc.</div>
          <hr/>
          <FormGroup controlId="formControlsTextarea">
            <ControlLabel>Feature Selection</ControlLabel>
            <Field
              rows="10"
              name="feature_selection"
              component={renderTextArea}
            />
          </FormGroup>
          <hr/>
          <Row>
            <Col xs={6}>
              <FormGroup controlId="formControlsSelect">
                <ControlLabel>Run this export on an automated schedule:</ControlLabel>
                <Field
                  name="schedule_period"
                  component={renderScheduleSelect}
                />
              </FormGroup>
            </Col>
            <Col xs={5} xsOffset={1}>
              <FormGroup controlId="formControlsSelect">
                <ControlLabel>At time:</ControlLabel>
                <Field
                  name="schedule_hour"
                  component={renderTimeSelect}
                />
              </FormGroup>
            </Col>
          </Row>
          <Row>
            <Col xs={5}>
              <FormGroup controlId="formControlsFormats">
                <ControlLabel>File Formats</ControlLabel>
                <Field
                  name="shp"
                  description="ESRI Shapefiles"
                  component={renderCheckbox}
                />
                <Field
                  name="geopackage"
                  description="GeoPackage"
                  component={renderCheckbox}
                />
                <Field
                  name="garmin"
                  description="Garmin .IMG"
                  component={renderCheckbox}
                />
                <Field
                  name="kml"
                  description=".KMZ"
                  component={renderCheckbox}
                />
                <Field
                  name="pbf"
                  description="OpenStreetMap .PBF"
                  component={renderCheckbox}
                />
              </FormGroup>
            </Col>
            <Col xs={7}>
              <Panel>
                This will immediately create 5 datasets on HDX:
                <ul>
                  <li><code>hotosm_senegal_admin_boundaries</code></li>
                  <li><code>hotosm_senegal_buildings</code></li>
                  <li><code>hotosm_senegal_points_of_interest</code></li>
                  <li><code>hotosm_senegal_roads</code></li>
                  <li><code>hotosm_senegal_waterways</code></li>
                </ul>
                <Button bsStyle="primary" bsSize="large" type="submit" disabled={pristine || submitting} onClick={handleSubmit} block>
                  Create Datasets + Run Export
                </Button>
              </Panel>
            </Col>
          </Row>
        </form>
      </div>
    )
  }
}


const mapStateToProps = state => {
  return {
    initialValues: {
      aoiInfo: state.aoiInfo
    },
    aoiInfo: state.aoiInfo
  };
};

const mapDispatchToProps = dispatch => {
  return {
    // setDatasetPrefix: prefix => {
    //   dispatch(actions.setDatasetPrefix(prefix));
    // }
  }
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(form(HDXCreateForm));
