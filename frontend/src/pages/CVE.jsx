import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function CVE() {
  const { token } = useAuth();
  const [cves, setCves] = useState([]);

  useEffect(() => {
    api.cves(token).then(setCves).catch(() => {});
  }, [token]);

  return (
    <div className="page">
      <h1>CVE Learning Section</h1>
      <p className="subtitle">Learn about famous real-world vulnerabilities before attempting related challenges.</p>
      <div className="cve-grid">
        {cves.map((cve) => (
          <div key={cve.cve_id} className="cve-card">
            <div className="cve-card-top">
              <h3>{cve.name}</h3>
              <span className="cve-year">{cve.year}</span>
            </div>
            <p className="cve-id">{cve.cve_id}</p>
            <p>{cve.description}</p>
            <span className="category-tag">{cve.related_category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
