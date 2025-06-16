import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Authentication
  const [loginData, setLoginData] = useState({ username: '', password: '' });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    if (token && user) {
      setCurrentUser(JSON.parse(user));
      fetchDashboardData();
    }
  }, []);

  const fetchWithAuth = async (url, options = {}) => {
    const token = localStorage.getItem('access_token');
    return fetch(`${API_BASE_URL}${url}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData),
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setCurrentUser(data.user);
        fetchDashboardData();
      } else {
        alert('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login error');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setCases([]);
    setSelectedCase(null);
  };

  const fetchDashboardData = async () => {
    try {
      const [casesRes, usersRes, statsRes] = await Promise.all([
        fetchWithAuth('/api/cases'),
        fetchWithAuth('/api/users'),
        fetchWithAuth('/api/dashboard/stats'),
      ]);

      if (casesRes.ok) setCases(await casesRes.json());
      if (usersRes.ok) setUsers(await usersRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const handleWorkflowAction = async (caseId, action, assignedTo = null, comment = '') => {
    setLoading(true);
    try {
      const response = await fetchWithAuth(`/api/cases/${caseId}/workflow`, {
        method: 'POST',
        body: JSON.stringify({
          case_id: caseId,
          action,
          assigned_to: assignedTo,
          comment,
        }),
      });

      if (response.ok) {
        await fetchDashboardData();
        if (selectedCase && selectedCase.id === caseId) {
          const caseRes = await fetchWithAuth(`/api/cases/${caseId}`);
          if (caseRes.ok) setSelectedCase(await caseRes.json());
        }
        alert(`Case ${action} successfully`);
      } else {
        alert('Action failed');
      }
    } catch (error) {
      console.error('Workflow action error:', error);
      alert('Action error');
    }
    setLoading(false);
  };

  const getCaseTypeLabel = (type) => {
    const labels = {
      birth_registration: 'Birth Registration',
      business_registration: 'Business Registration',
      land_registration: 'Land Registration',
    };
    return labels[type] || type;
  };

  const getStatusBadge = (status) => {
    const statusStyles = {
      submitted: 'bg-blue-100 text-blue-800',
      assigned: 'bg-yellow-100 text-yellow-800',
      under_review: 'bg-purple-100 text-purple-800',
      pending_documents: 'bg-orange-100 text-orange-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Case Management System
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Sign in to access your dashboard
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleLogin}>
            <div className="rounded-md shadow-sm -space-y-px">
              <div>
                <input
                  type="text"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Username"
                  value={loginData.username}
                  onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                />
              </div>
              <div>
                <input
                  type="password"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
            
            <div className="text-sm text-gray-600">
              <p><strong>Demo Accounts:</strong></p>
              <p>Admin: admin / admin123</p>
              <p>Registrar: registrar1 / reg123</p>
              <p>Assistant: assistant1 / ass123</p>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Case Management System</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                {currentUser.full_name} ({currentUser.role})
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Navigation Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            {['dashboard', 'cases', 'case-detail'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab === 'case-detail' ? 'Case Detail' : tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
            
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-bold">T</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Cases</dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {Object.values(stats.by_status || {}).reduce((a, b) => a + b, 0)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-bold">P</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Pending</dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {(stats.by_status?.submitted || 0) + (stats.by_status?.assigned || 0)}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-bold">A</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Approved</dt>
                        <dd className="text-lg font-medium text-gray-900">
                          {stats.by_status?.approved || 0}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Cases */}
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Cases</h3>
              </div>
              <ul className="divide-y divide-gray-200">
                {cases.slice(0, 5).map((case_) => (
                  <li key={case_.id}>
                    <div className="px-4 py-4 flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          {getStatusBadge(case_.status)}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {case_.case_number}
                          </div>
                          <div className="text-sm text-gray-500">
                            {getCaseTypeLabel(case_.case_type)}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          setSelectedCase(case_);
                          setActiveTab('case-detail');
                        }}
                        className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                      >
                        View
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Cases Tab */}
        {activeTab === 'cases' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">All Cases</h2>
              <button
                onClick={fetchDashboardData}
                className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
              >
                Refresh
              </button>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {cases.map((case_) => (
                  <li key={case_.id}>
                    <div className="px-4 py-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          {getStatusBadge(case_.status)}
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {case_.case_number}
                            </div>
                            <div className="text-sm text-gray-500">
                              {getCaseTypeLabel(case_.case_type)} • Created: {new Date(case_.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {case_.status === 'submitted' && ['registrar', 'supervisor'].includes(currentUser.role) && (
                            <select
                              onChange={(e) => {
                                if (e.target.value) {
                                  handleWorkflowAction(case_.id, 'assign', e.target.value);
                                }
                              }}
                              className="text-sm border border-gray-300 rounded px-2 py-1"
                              defaultValue=""
                            >
                              <option value="">Assign to...</option>
                              {users.filter(u => u.role !== 'supervisor').map(user => (
                                <option key={user.id} value={user.id}>
                                  {user.full_name} ({user.role})
                                </option>
                              ))}
                            </select>
                          )}
                          <button
                            onClick={() => {
                              setSelectedCase(case_);
                              setActiveTab('case-detail');
                            }}
                            className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                          >
                            View Details
                          </button>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Case Detail Tab */}
        {activeTab === 'case-detail' && selectedCase && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">
                Case Details: {selectedCase.case_number}
              </h2>
              {getStatusBadge(selectedCase.status)}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Case Information */}
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Case Information</h3>
                </div>
                <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                  <dl className="sm:divide-y sm:divide-gray-200">
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Case Type</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {getCaseTypeLabel(selectedCase.case_type)}
                      </dd>
                    </div>
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Created</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {new Date(selectedCase.created_at).toLocaleString()}
                      </dd>
                    </div>
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Status</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        {selectedCase.status.replace('_', ' ').toUpperCase()}
                      </dd>
                    </div>
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                      <dt className="text-sm font-medium text-gray-500">Submitted Data</dt>
                      <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                        <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto">
                          {JSON.stringify(selectedCase.submitter_data, null, 2)}
                        </pre>
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>

              {/* Workflow Actions */}
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Workflow Actions</h3>
                </div>
                <div className="border-t border-gray-200 p-4 space-y-4">
                  {selectedCase.status === 'assigned' && (
                    <button
                      onClick={() => handleWorkflowAction(selectedCase.id, 'review')}
                      className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                      disabled={loading}
                    >
                      Start Review
                    </button>
                  )}
                  
                  {selectedCase.status === 'under_review' && (
                    <div className="space-y-2">
                      <button
                        onClick={() => handleWorkflowAction(selectedCase.id, 'approve')}
                        className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                        disabled={loading}
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleWorkflowAction(selectedCase.id, 'reject')}
                        className="w-full bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                        disabled={loading}
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleWorkflowAction(selectedCase.id, 'request_documents')}
                        className="w-full bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700"
                        disabled={loading}
                      >
                        Request Documents
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Workflow History */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Workflow History</h3>
              </div>
              <div className="border-t border-gray-200">
                <ul className="divide-y divide-gray-200">
                  {selectedCase.workflow_history?.map((entry, index) => (
                    <li key={index} className="px-4 py-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {entry.action.replace('_', ' ').toUpperCase()}
                          </div>
                          <div className="text-sm text-gray-500">
                            {entry.performed_by_name || 'System'} • {new Date(entry.timestamp).toLocaleString()}
                          </div>
                          {entry.comment && (
                            <div className="text-sm text-gray-600 mt-1">
                              Comment: {entry.comment}
                            </div>
                          )}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;