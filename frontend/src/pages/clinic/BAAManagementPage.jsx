import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { Card, Button, Checkbox, Input, Typography, Spin, Alert } from "antd";
import api from "../../lib/api";

const { Title, Paragraph, Text } = Typography;

const BAAManagementPage = () => {
  const [baaTemplate, setBaaTemplate] = useState("");
  const [baaStatus, setBaaStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [signatureName, setSignatureName] = useState("");
  const [signatureTitle, setSignatureTitle] = useState("");
  const [confirm, setConfirm] = useState(false);
  const [signing, setSigning] = useState(false);

  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [templateRes, statusRes] = await Promise.all([
          api.get("/baa/template"),
          api.get("/baa/status"),
        ]);
        setBaaTemplate(templateRes.data);
        setBaaStatus(statusRes.data);
      } catch (err) {
        setError("Failed to load BAA information. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleSign = async () => {
    if (!signatureName || !signatureTitle || !confirm) {
      setError("Please fill in all fields and confirm your agreement.");
      return;
    }

    try {
      setSigning(true);
      setError(null);

      const response = await api.post("/baa/sign", {
        signature_name: signatureName,
        signature_title: signatureTitle,
        confirm: confirm,
      });

      setBaaStatus({
        is_signed: true,
        signed_at: response.data.signed_at,
        signed_by: user.email,
        signature_name: response.data.signature_name,
        signature_title: signatureTitle,
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to sign BAA. Please try again.");
    } finally {
      setSigning(false);
    }
  };

  if (loading) {
    return <Spin size="large" />;
  }

  if (error && !baaTemplate) {
    return <Alert message="Error" description={error} type="error" showIcon />;
  }

  return (
    <Card title="Business Associate Agreement (BAA)">
      {baaStatus?.is_signed ? (
        <BAASignedView status={baaStatus} />
      ) : (
        <BAASigningView
          baaTemplate={baaTemplate}
          signatureName={signatureName}
          setSignatureName={setSignatureName}
          signatureTitle={signatureTitle}
          setSignatureTitle={setSignatureTitle}
          confirm={confirm}
          setConfirm={setConfirm}
          handleSign={handleSign}
          signing={signing}
          error={error}
        />
      )}
    </Card>
  );
};

const BAASignedView = ({ status }) => (
  <div>
    <Title level={4}>BAA Signed</Title>
    <Alert
      message="This Business Associate Agreement has been signed."
      type="success"
      showIcon
    />
    <Paragraph style={{ marginTop: 20 }}>
      <Text strong>Signed By:</Text> {status.signature_name} ({status.signed_by})
    </Paragraph>
    <Paragraph>
      <Text strong>Title:</Text> {status.signature_title}
    </Paragraph>
    <Paragraph>
      <Text strong>Signed At:</Text> {new Date(status.signed_at).toLocaleString()}
    </Paragraph>
  </div>
);

const BAASigningView = ({
  baaTemplate,
  signatureName,
  setSignatureName,
  signatureTitle,
  setSignatureTitle,
  confirm,
  setConfirm,
  handleSign,
  signing,
  error,
}) => (
  <div>
    <Title level={4}>Please Sign the BAA</Title>
    <Paragraph>
      To ensure HIPAA compliance, your organization must sign this Business
      Associate Agreement.
    </Paragraph>

    <Card style={{ maxHeight: 400, overflowY: "auto", marginBottom: 20 }}>
      <pre>{baaTemplate}</pre>
    </Card>

    <div style={{ marginBottom: 20 }}>
      <Input
        placeholder="Your Full Name"
        value={signatureName}
        onChange={(e) => setSignatureName(e.target.value)}
        style={{ marginBottom: 10 }}
      />
      <Input
        placeholder="Your Title"
        value={signatureTitle}
        onChange={(e) => setSignatureTitle(e.target.value)}
      />
    </div>

    <Checkbox checked={confirm} onChange={(e) => setConfirm(e.target.checked)}>
      I have read, understood, and agree to the terms of this Business Associate
      Agreement.
    </Checkbox>

    {error && (
      <Alert
        message={error}
        type="error"
        showIcon
        style={{ margin: "20px 0" }}
      />
    )}

    <Button
      type="primary"
      onClick={handleSign}
      loading={signing}
      disabled={!signatureName || !signatureTitle || !confirm}
      style={{ marginTop: 20 }}
    >
      Sign Agreement
    </Button>
  </div>
);

export default BAAManagementPage;

