Text file: TelegramHub.jsx
Reading lines: 1-500 (file has 841 lines)
Latest content with line numbers:
1	import React, { useState, useEffect, useRef } from 'react';
2	import { 
3	  Send, Search, User, Phone, Calendar, Clock, CheckCircle, AlertCircle,
4	  MessageCircle, Users, Key, BarChart3, Copy, QrCode, Plus, X, Link2, Unlink
5	} from 'lucide-react';
6	
7	/**
8	 * Telegram Hub - Complete Telegram Management Interface
9	 * 
10	 * Features:
11	 * - Conversations: View and manage all Telegram conversations
12	 * - Users: Manage Telegram users and patient linkage
13	 * - Invite Codes: Generate and manage invite codes
14	 * - Analytics: View Telegram usage statistics
15	 */
16	const TelegramHub = () => {
17	  // Tab state
18	  const [activeTab, setActiveTab] = useState('conversations');
19	  
20	  // Conversations state
21	  const [conversations, setConversations] = useState([]);
22	  const [selectedConversation, setSelectedConversation] = useState(null);
23	  const [messages, setMessages] = useState([]);
24	  const [messageInput, setMessageInput] = useState('');
25	  const [searchQuery, setSearchQuery] = useState('');
26	  
27	  // Users state
28	  const [users, setUsers] = useState([]);
29	  const [selectedUser, setSelectedUser] = useState(null);
30	  
31	  // Invite codes state
32	  const [inviteCodes, setInviteCodes] = useState([]);
33	  const [newInviteForm, setNewInviteForm] = useState({
34	    max_uses: 1,
35	    expires_in_days: 7,
36	    notes: ''
37	  });
38	  
39	  // Analytics state
40	  const [analytics, setAnalytics] = useState({
41	    total_users: 0,
42	    active_conversations: 0,
43	    messages_today: 0,
44	    avg_response_time: 0
45	  });
46	  
47	  // Loading states
48	  const [loading, setLoading] = useState(true);
49	  const [actionLoading, setActionLoading] = useState(false);
50	  
51	  // Refs
52	  const messagesEndRef = useRef(null);
53	
54	  // Fetch data on mount and tab change
55	  useEffect(() => {
56	    fetchData();
57	    
58	    // Set up polling for active tab
59	    const interval = setInterval(fetchData, 5000);
60	    return () => clearInterval(interval);
61	  }, [activeTab]);
62	
63	  // Scroll to bottom when messages change
64	  useEffect(() => {
65	    scrollToBottom();
66	  }, [messages]);
67	
68	  const scrollToBottom = () => {
69	    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
70	  };
71	
72	  const fetchData = async () => {
73	    try {
74	      const token = localStorage.getItem('token');
75	      const headers = { 'Authorization': `Bearer ${token}` };
76	
77	      if (activeTab === 'conversations') {
78	        const response = await fetch('/api/v1/telegram/conversations', { headers });
79	        const data = await response.json();
80	        setConversations(data.conversations || data || []);
81	      } else if (activeTab === 'users') {
82	        const response = await fetch('/api/v1/telegram/users', { headers });
83	        const data = await response.json();
84	        setUsers(data.users || data || []);
85	      } else if (activeTab === 'invites') {
86	        const response = await fetch('/api/v1/telegram/invite-codes', { headers });
87	        const data = await response.json();
88	        setInviteCodes(data.invite_codes || data || []);
89	      } else if (activeTab === 'analytics') {
90	        const response = await fetch('/api/v1/telegram/stats', { headers });
91	        const data = await response.json();
92	        setAnalytics(data || {});
93	      }
94	      
95	      setLoading(false);
96	    } catch (error) {
97	      console.error('Error fetching data:', error);
98	      setLoading(false);
99	    }
100	  };
101	
102	  const fetchMessages = async (conversationId) => {
103	    try {
104	      const response = await fetch(`/api/v1/telegram/conversations/${conversationId}/messages`, {
105	        headers: {
106	          'Authorization': `Bearer ${localStorage.getItem('token')}`
107	        }
108	      });
109	      const data = await response.json();
110	      setMessages(data.messages || []);
111	    } catch (error) {
112	      console.error('Error fetching messages:', error);
113	    }
114	  };
115	
116	  const handleConversationSelect = (conversation) => {
117	    setSelectedConversation(conversation);
118	    fetchMessages(conversation.id);
119	  };
120	
121	  const handleSendMessage = async (e) => {
122	    e.preventDefault();
123	    if (!messageInput.trim() || !selectedConversation) return;
124	
125	    try {
126	      const response = await fetch('/api/v1/telegram/send', {
127	        method: 'POST',
128	        headers: {
129	          'Content-Type': 'application/json',
130	          'Authorization': `Bearer ${localStorage.getItem('token')}`
131	        },
132	        body: JSON.stringify({
133	          chat_id: selectedConversation.telegram_chat_id,
134	          message: messageInput
135	        })
136	      });
137	
138	      if (response.ok) {
139	        setMessageInput('');
140	        fetchMessages(selectedConversation.id);
141	      }
142	    } catch (error) {
143	      console.error('Error sending message:', error);
144	    }
145	  };
146	
147	  const handleCreateInviteCode = async (e) => {
148	    e.preventDefault();
149	    setActionLoading(true);
150	
151	    try {
152	      const response = await fetch('/api/v1/telegram/invite-codes', {
153	        method: 'POST',
154	        headers: {
155	          'Content-Type': 'application/json',
156	          'Authorization': `Bearer ${localStorage.getItem('token')}`
157	        },
158	        body: JSON.stringify(newInviteForm)
159	      });
160	
161	      if (response.ok) {
162	        setNewInviteForm({ max_uses: 1, expires_in_days: 7, notes: '' });
163	        fetchData();
164	      }
165	    } catch (error) {
166	      console.error('Error creating invite code:', error);
167	    } finally {
168	      setActionLoading(false);
169	    }
170	  };
171	
172	  const handleCopyInviteCode = (code) => {
173	    navigator.clipboard.writeText(code);
174	    // TODO: Show toast notification
175	  };
176	
177	  const handleLinkUser = async (userId, patientId) => {
178	    setActionLoading(true);
179	    try {
180	      // TODO: Implement user linking API call
181	      console.log('Linking user', userId, 'to patient', patientId);
182	      fetchData();
183	    } catch (error) {
184	      console.error('Error linking user:', error);
185	    } finally {
186	      setActionLoading(false);
187	    }
188	  };
189	
190	  const handleUnlinkUser = async (userId) => {
191	    setActionLoading(true);
192	    try {
193	      const response = await fetch(`/api/v1/telegram/users/${userId}`, {
194	        method: 'DELETE',
195	        headers: {
196	          'Authorization': `Bearer ${localStorage.getItem('token')}`
197	        }
198	      });
199	
200	      if (response.ok) {
201	        fetchData();
202	      }
203	    } catch (error) {
204	      console.error('Error unlinking user:', error);
205	    } finally {
206	      setActionLoading(false);
207	    }
208	  };
209	
210	  const filteredConversations = conversations.filter(conv =>
211	    conv.patient_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
212	    conv.telegram_username?.toLowerCase().includes(searchQuery.toLowerCase())
213	  );
214	
215	  const filteredUsers = users.filter(user =>
216	    user.telegram_username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
217	    user.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
218	    user.last_name?.toLowerCase().includes(searchQuery.toLowerCase())
219	  );
220	
221	  const formatTime = (timestamp) => {
222	    if (!timestamp) return '';
223	    const date = new Date(timestamp);
224	    const now = new Date();
225	    const diffMs = now - date;
226	    const diffMins = Math.floor(diffMs / 60000);
227	    
228	    if (diffMins < 1) return 'עכשיו';
229	    if (diffMins < 60) return `לפני ${diffMins} דקות`;
230	    if (diffMins < 1440) return `לפני ${Math.floor(diffMins / 60)} שעות`;
231	    return date.toLocaleDateString('he-IL');
232	  };
233	
234	  const formatDate = (dateString) => {
235	    if (!dateString) return '';
236	    return new Date(dateString).toLocaleDateString('he-IL');
237	  };
238	
239	  // Tab navigation
240	  const tabs = [
241	    { id: 'conversations', label: 'שיחות', icon: MessageCircle },
242	    { id: 'users', label: 'משתמשים', icon: Users },
243	    { id: 'invites', label: 'קודי הזמנה', icon: Key },
244	    { id: 'analytics', label: 'סטטיסטיקה', icon: BarChart3 }
245	  ];
246	
247	  return (
248	    <div className="h-screen flex flex-col bg-gray-50">
249	      {/* Header */}
250	      <div className="bg-white border-b border-gray-200 px-6 py-4">
251	        <h1 className="text-2xl font-bold text-gray-900">Telegram Hub</h1>
252	        <p className="text-sm text-gray-600 mt-1">ניהול שיחות Telegram ומשתמשים</p>
253	      </div>
254	
255	      {/* Tabs */}
256	      <div className="bg-white border-b border-gray-200">
257	        <div className="flex gap-1 px-6">
258	          {tabs.map((tab) => {
259	            const Icon = tab.icon;
260	            return (
261	              <button
262	                key={tab.id}
263	                onClick={() => setActiveTab(tab.id)}
264	                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
265	                  activeTab === tab.id
266	                    ? 'border-blue-600 text-blue-600'
267	                    : 'border-transparent text-gray-600 hover:text-gray-900'
268	                }`}
269	              >
270	                <Icon size={20} />
271	                <span className="font-medium">{tab.label}</span>
272	              </button>
273	            );
274	          })}
275	        </div>
276	      </div>
277	
278	      {/* Tab Content */}
279	      <div className="flex-1 overflow-hidden">
280	        {activeTab === 'conversations' && (
281	          <ConversationsTab
282	            conversations={filteredConversations}
283	            selectedConversation={selectedConversation}
284	            messages={messages}
285	            messageInput={messageInput}
286	            searchQuery={searchQuery}
287	            loading={loading}
288	            onConversationSelect={handleConversationSelect}
289	            onSendMessage={handleSendMessage}
290	            onMessageInputChange={setMessageInput}
291	            onSearchChange={setSearchQuery}
292	            formatTime={formatTime}
293	            messagesEndRef={messagesEndRef}
294	          />
295	        )}
296	
297	        {activeTab === 'users' && (
298	          <UsersTab
299	            users={filteredUsers}
300	            searchQuery={searchQuery}
301	            loading={loading}
302	            actionLoading={actionLoading}
303	            onSearchChange={setSearchQuery}
304	            onLinkUser={handleLinkUser}
305	            onUnlinkUser={handleUnlinkUser}
306	            formatTime={formatTime}
307	          />
308	        )}
309	
310	        {activeTab === 'invites' && (
311	          <InviteCodesTab
312	            inviteCodes={inviteCodes}
313	            newInviteForm={newInviteForm}
314	            loading={loading}
315	            actionLoading={actionLoading}
316	            onFormChange={setNewInviteForm}
317	(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)