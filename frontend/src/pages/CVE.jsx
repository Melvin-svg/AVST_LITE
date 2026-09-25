import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const CATEGORIES = [
  "All",
  "Web Security",
  "Reverse Engineering",
  "Cryptography",
  "Network",
  "General Security",
];

const TABS = [
  { id: "all", label: "All Active Threats", icon: "🌐" },
  { id: "2026", label: "2026 Exploits", icon: "⚡" },
  { id: "ransomware", label: "Ransomware Vectors", icon: "☣️" },
  { id: "landmarks", label: "Landmark CVEs", icon: "🏛️" },
];

export default function CVE() {
  const { token } = useAuth();
  const [cves, setCves] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // Filters
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [activeTab, setActiveTab] = useState("all");
  const [expandedRemediation, setExpandedRemediation] = useState({});

  const loadData = async (forceRefresh = false) => {
    if (forceRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const [cveList, statsData] = await Promise.all([
        api.cves(token, { limit: 120, refresh: forceRefresh }),
        api.cveStats(token).catch(() => null),
      ]);
      setCves(cveList);
      if (statsData) setStats(statsData);
    } catch (err) {
      console.error("Failed to load CVE data:", err);
      setError("Unable to sync live CVE data. Showing cached vulnerabilities if available.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData(false);
  }, [token]);

  const toggleRemediation = (cveId) => {
    setExpandedRemediation((prev) => ({
      ...prev,
      [cveId]: !prev[cveId],
    }));
  };

  // Filtered list
  const filteredCves = useMemo(() => {
    return cves.filter((cve) => {
      // Tab filter
      if (activeTab === "2026" && cve.year !== 2026) return false;
      if (activeTab === "ransomware" && cve.ransomware_use !== "Known") return false;
      if (activeTab === "landmarks" && cve.is_realtime) return false;

      // Category filter
      if (
        selectedCategory !== "All" &&
        cve.related_category.toLowerCase() !== selectedCategory.toLowerCase()
      ) {
        return false;
      }

      // Search filter
      if (search.trim()) {
        const query = search.trim().toLowerCase();
        const inId = cve.cve_id.toLowerCase().includes(query);
        const inName = cve.name.toLowerCase().includes(query);
        const inDesc = cve.description.toLowerCase().includes(query);
        const inVendor = cve.vendor && cve.vendor.toLowerCase().includes(query);
        const inProduct = cve.product && cve.product.toLowerCase().includes(query);
        const inCwe = cve.cwes && cve.cwes.some((c) => c.toLowerCase().includes(query));
        if (!inId && !inName && !inDesc && !inVendor && !inProduct && !inCwe) {
          return false;
        }
      }

      return true;
    });
  }, [cves, activeTab, selectedCategory, search]);

  return (
    <div className="page cve-page">
      {/* Header with live feed indicator & Sync */}
      <div className="cve-hero">
        <div className="cve-hero-text">
          <div className="cve-live-badge-wrap">
            <span className="live-dot-pulse"></span>
            <span className="cve-live-badge-label">
              LIVE CISA KEV INTELLIGENCE FEED
            </span>
            {stats?.last_synced && (
              <span className="cve-live-synced">Synced: {stats.last_synced}</span>
            )}
          </div>
          <h1>Real-Time Vulnerability Intelligence</h1>
          <p className="subtitle">
            Study real-time vulnerabilities currently being exploited in the wild.
            Sourced dynamically from official security feeds, categorized by attack surface,
            and linked directly to hands-on CTF labs.
          </p>
        </div>

        <button
          className={`cve-sync-btn ${refreshing ? "syncing" : ""}`}
          onClick={() => loadData(true)}
          disabled={refreshing || loading}
          title="Force sync latest real-time feeds"
        >
          <span className="sync-icon">🔄</span>
          <span>{refreshing ? "Syncing Feed..." : "Sync Live Feed"}</span>
        </button>
      </div>

      {/* Telemetry KPI Cards */}
      <div className="cve-stats-grid">
        <div className="cve-stat-card">
          <div className="cve-stat-icon">🛡️</div>
          <div className="cve-stat-info">
            <span className="cve-stat-value">
              {stats?.total_tracked ? stats.total_tracked.toLocaleString() : "1,720+"}
            </span>
            <span className="cve-stat-label">Active Exploited CVEs</span>
          </div>
        </div>

        <div className="cve-stat-card">
          <div className="cve-stat-icon">⚡</div>
          <div className="cve-stat-info">
            <span className="cve-stat-value">{stats?.count_2026 ?? "150+"}</span>
            <span className="cve-stat-label">2026 Zero-Days & Exploits</span>
          </div>
        </div>

        <div className="cve-stat-card">
          <div className="cve-stat-icon">☣️</div>
          <div className="cve-stat-info">
            <span className="cve-stat-value">{stats?.ransomware_count ?? "365"}</span>
            <span className="cve-stat-label">Ransomware Vectors</span>
          </div>
        </div>

        <div className="cve-stat-card">
          <div className="cve-stat-icon">📡</div>
          <div className="cve-stat-info">
            <span className="cve-stat-value">Live Stream</span>
            <span className="cve-stat-label">Automated Ingestion</span>
          </div>
        </div>
      </div>

      {/* Control Bar: Search & Tabs */}
      <div className="cve-controls-panel">
        <div className="cve-search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search CVE ID (e.g. CVE-2026), vendor (Microsoft, Adobe), product, or CWE..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="clear-search-btn" onClick={() => setSearch("")}>
              ✕
            </button>
          )}
        </div>

        {/* Tab Filters */}
        <div className="cve-tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`cve-tab-btn ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Category Pills */}
      <div className="cve-category-pills">
        <span className="category-filter-label">Category:</span>
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            className={`pill-btn ${selectedCategory === cat ? "active" : ""}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Feedback banner if error */}
      {error && (
        <div className="cve-alert-banner">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* Loading Skeletons */}
      {loading ? (
        <div className="cve-grid">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="cve-card cve-skeleton-card">
              <div className="skeleton-line shimmer" style={{ width: "30%", height: 16 }}></div>
              <div className="skeleton-line shimmer" style={{ width: "80%", height: 22 }}></div>
              <div className="skeleton-line shimmer" style={{ width: "100%", height: 60 }}></div>
              <div className="skeleton-line shimmer" style={{ width: "50%", height: 18 }}></div>
            </div>
          ))}
        </div>
      ) : filteredCves.length === 0 ? (
        <div className="cve-empty-state">
          <div className="empty-icon">🔎</div>
          <h3>No vulnerabilities found</h3>
          <p>Try refining your search query or switching to another category or tab.</p>
          <button
            className="btn btn-secondary"
            onClick={() => {
              setSearch("");
              setSelectedCategory("All");
              setActiveTab("all");
            }}
          >
            Reset All Filters
          </button>
        </div>
      ) : (
        <div className="cve-results-summary">
          <span>
            Showing <strong>{filteredCves.length}</strong> vulnerabilities
            {selectedCategory !== "All" && ` in ${selectedCategory}`}
            {activeTab !== "all" && ` (${TABS.find((t) => t.id === activeTab)?.label})`}
          </span>
        </div>
      )}

      {/* CVE Grid */}
      {!loading && filteredCves.length > 0 && (
        <div className="cve-grid">
          {filteredCves.map((cve) => {
            const isExpanded = !!expandedRemediation[cve.cve_id];
            const isRecent = cve.year === 2026;
            const isRansomware = cve.ransomware_use === "Known";

            return (
              <div key={cve.cve_id} className={`cve-card ${isRecent ? "recent-threat" : ""}`}>
                {/* Top header row */}
                <div className="cve-card-top">
                  <div className="cve-id-group">
                    <a
                      href={cve.nvd_url || `https://nvd.nist.gov/vuln/detail/${cve.cve_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="cve-id-badge"
                      title="View official NVD vulnerability entry"
                    >
                      <span>{cve.cve_id}</span>
                      <span className="ext-icon">↗</span>
                    </a>

                    {isRecent && <span className="threat-badge threat-new">⚡ 2026</span>}
                    {isRansomware && (
                      <span className="threat-badge threat-ransomware" title="Known weaponized ransomware vector">
                        ☣️ Ransomware
                      </span>
                    )}
                  </div>

                  <div className="cve-badges-right">
                    <span
                      className={`severity-badge ${
                        cve.severity === "Critical" ? "sev-critical" : "sev-high"
                      }`}
                    >
                      {cve.severity || "High"}
                    </span>
                    <span className="cve-date-badge">
                      {cve.date_added ? `Added ${cve.date_added}` : `${cve.year}`}
                    </span>
                  </div>
                </div>

                {/* Title */}
                <h3 className="cve-title">{cve.name}</h3>

                {/* Vendor / Product pill */}
                {(cve.vendor || cve.product) && (
                  <div className="cve-meta-tags">
                    {cve.vendor && <span className="meta-vendor">🏢 {cve.vendor}</span>}
                    {cve.product && <span className="meta-product">📦 {cve.product}</span>}
                  </div>
                )}

                {/* Description */}
                <p className="cve-description">{cve.description}</p>

                {/* CWE tags */}
                {cve.cwes && cve.cwes.length > 0 && (
                  <div className="cve-cwes">
                    {cve.cwes.map((cwe) => (
                      <span key={cwe} className="cwe-tag">
                        {cwe}
                      </span>
                    ))}
                  </div>
                )}

                {/* Remediation Action Callout */}
                {cve.required_action && (
                  <div className="cve-remediation-box">
                    <div
                      className="remediation-header"
                      onClick={() => toggleRemediation(cve.cve_id)}
                      role="button"
                      tabIndex={0}
                    >
                      <span>🛡️ Required Action / Mitigation</span>
                      <span className="toggle-chevron">{isExpanded ? "▲" : "▼"}</span>
                    </div>
                    {isExpanded && (
                      <p className="remediation-text">{cve.required_action}</p>
                    )}
                  </div>
                )}

                {/* Card Footer: Category + Action Links */}
                <div className="cve-card-footer">
                  <span className={`category-tag cat-${cve.related_category.replace(/\s+/g, "-").toLowerCase()}`}>
                    {cve.related_category}
                  </span>

                  <div className="cve-action-links">
                    {cve.vendor_advisory_url && (
                      <a
                        href={cve.vendor_advisory_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="cve-link-btn"
                        title="View vendor official advisory"
                      >
                        Advisory ↗
                      </a>
                    )}
                    <Link
                      to={`/challenges?category=${encodeURIComponent(
                        cve.related_category === "General Security"
                          ? "Web Security"
                          : cve.related_category
                      )}`}
                      className="cve-practice-btn"
                      title="Practice hands-on challenge related to this vulnerability"
                    >
                      Practice Lab →
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
