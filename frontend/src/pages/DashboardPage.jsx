import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { LogOut, Sparkles, MessageSquare, Calendar, DollarSign, Stethoscope, ArrowLeft } from 'lucide-react'

export default function DashboardPage({ user, onLogout }) {
  const agents = [
    {
      name: 'Dana',
      role: 'Coordinator',
      description: 'Routes conversations and coordinates other agents',
      icon: MessageSquare,
      color: 'from-blue-500 to-blue-600',
      status: 'active',
    },
    {
      name: 'Dr. Michal',
      role: 'Dentist',
      description: 'Answers medical questions and provides treatment information',
      icon: Stethoscope,
      color: 'from-purple-500 to-purple-600',
      status: 'active',
    },
    {
      name: 'Yosef',
      role: 'Accountant',
      description: 'Handles billing, payments, and financial inquiries',
      icon: DollarSign,
      color: 'from-green-500 to-green-600',
      status: 'active',
    },
    {
      name: 'Sarah',
      role: 'Scheduler',
      description: 'Manages appointments and scheduling',
      icon: Calendar,
      color: 'from-pink-500 to-pink-600',
      status: 'active',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-xl">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                DentalAI Dashboard
              </h1>
              <p className="text-sm text-gray-600">Manage your AI agents and conversations</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/chat">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Chat
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <Avatar>
                <AvatarFallback className="bg-gradient-to-br from-blue-600 to-purple-600 text-white">
                  {user?.full_name?.charAt(0) || 'U'}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium">{user?.full_name || 'User'}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={onLogout}>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Welcome back, {user?.full_name || 'User'}!</h2>
          <p className="text-gray-600">Here's an overview of your AI dental assistants</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Total Agents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">4</div>
              <p className="text-xs text-gray-500 mt-1">All systems operational</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Active Conversations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">0</div>
              <p className="text-xs text-gray-500 mt-1">Start a new chat</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Response Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">2.5s</div>
              <p className="text-xs text-gray-500 mt-1">Average response time</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Satisfaction</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">98%</div>
              <p className="text-xs text-gray-500 mt-1">User satisfaction rate</p>
            </CardContent>
          </Card>
        </div>

        {/* AI Agents */}
        <div>
          <h3 className="text-2xl font-bold mb-4">Your AI Agents</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {agents.map((agent, index) => {
              const Icon = agent.icon
              return (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`bg-gradient-to-br ${agent.color} p-3 rounded-xl`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <CardTitle>{agent.name}</CardTitle>
                          <CardDescription>{agent.role}</CardDescription>
                        </div>
                      </div>
                      <Badge variant="success" className="bg-green-100 text-green-800">
                        {agent.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600">{agent.description}</p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h3 className="text-2xl font-bold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/chat">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="pt-6">
                  <MessageSquare className="w-8 h-8 mb-3 text-blue-600" />
                  <h4 className="font-semibold mb-1">Start New Chat</h4>
                  <p className="text-sm text-gray-600">Begin a conversation with our AI agents</p>
                </CardContent>
              </Card>
            </Link>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer opacity-50">
              <CardContent className="pt-6">
                <Calendar className="w-8 h-8 mb-3 text-purple-600" />
                <h4 className="font-semibold mb-1">View Appointments</h4>
                <p className="text-sm text-gray-600">Coming soon</p>
              </CardContent>
            </Card>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer opacity-50">
              <CardContent className="pt-6">
                <DollarSign className="w-8 h-8 mb-3 text-green-600" />
                <h4 className="font-semibold mb-1">Billing & Payments</h4>
                <p className="text-sm text-gray-600">Coming soon</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
