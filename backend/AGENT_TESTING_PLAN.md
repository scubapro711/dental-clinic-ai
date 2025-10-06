# Agent Testing Plan - Task 1.5

**Date:** October 6, 2025  
**Objective:** Test all agents with OdooClient integration

---

## System Architecture

### Agents in System
1. **Supervisor** - Routes requests to specialized agents
2. **Alex** - Patient-facing interactions, appointments, medical triage
3. **CFO** - Financial analysis and insights
4. **Practice Admin** - Operations and scheduling management

### Agent Graph Flow
```
User Request → Supervisor → [Alex | CFO | Admin] → Supervisor → Response
```

---

## Test Scenarios

### 1. Individual Agent Tests

#### Alex Agent Tests
- ✅ Search for patients
- ✅ Create appointments
- ✅ Get available slots
- ✅ Get patient appointments
- ✅ Get patient invoices
- ✅ Update appointment status
- ✅ RBAC: Patient can only see own data
- ✅ RBAC: Doctor can see all patients

#### CFO Agent Tests
- ✅ Get revenue overview
- ✅ Analyze payment status
- ✅ Get top treatments
- ✅ Get outstanding invoices
- ✅ Analyze profitability
- ✅ Get financial trends
- ✅ RBAC: Only owner/CFO can access

#### Practice Admin Agent Tests
- ✅ Detect schedule conflicts
- ✅ Get available slots
- ✅ Reschedule appointments
- ✅ Get staff schedule
- ✅ Check room availability
- ✅ Optimize schedule
- ✅ Get operational metrics
- ✅ Cancel appointments
- ✅ RBAC: Only admin/owner can access

### 2. Agent Graph Tests

#### Supervisor Routing
- Test supervisor routes to correct agent
- Test supervisor forwards responses correctly
- Test supervisor doesn't paraphrase
- Test multi-turn conversations

#### Agent Communication
- Test Alex → Supervisor → Response
- Test CFO → Supervisor → Response
- Test Admin → Supervisor → Response
- Test context preservation between turns

#### Multi-Agent Scenarios
- Test request requiring multiple agents
- Test handoff between agents
- Test context sharing between agents

### 3. RBAC Tests

#### Role-Based Access Control
- Test patient role restrictions
- Test doctor role permissions
- Test admin role permissions
- Test owner role permissions
- Test permission denied messages
- Test access logging

### 4. Integration Tests

#### OdooClient Integration
- Test all agents use OdooClient correctly
- Test data consistency across agents
- Test error handling
- Test performance

#### Memory & State
- Test conversation history
- Test state persistence
- Test context preservation
- Test memory cleanup

---

## Test Execution Plan

### Phase 1: Individual Agent Tests (30 min)
1. Test Alex agent with OdooClient
2. Test CFO agent with OdooClient
3. Test Admin agent with OdooClient
4. Verify all tools work correctly

### Phase 2: Agent Graph Tests (30 min)
1. Test supervisor routing
2. Test agent communication
3. Test multi-turn conversations
4. Test context preservation

### Phase 3: RBAC Tests (20 min)
1. Test role restrictions
2. Test permission checks
3. Test access logging
4. Test error messages

### Phase 4: Integration Tests (20 min)
1. Test end-to-end scenarios
2. Test error handling
3. Test performance
4. Test edge cases

### Phase 5: Documentation (20 min)
1. Document test results
2. Create test report
3. Update progress tracking
4. Prepare for Task 1.6

---

## Success Criteria

### Must Pass
- ✅ All individual agent tests pass
- ✅ Supervisor routes correctly
- ✅ Agents use OdooClient correctly
- ✅ RBAC works as expected
- ✅ No data leaks between roles
- ✅ Error handling works correctly

### Nice to Have
- ✅ Multi-agent scenarios work
- ✅ Performance is acceptable
- ✅ Memory usage is reasonable
- ✅ Logs are comprehensive

---

## Test Files to Create

1. `test_alex_agent_odoo.py` - Alex agent tests
2. `test_cfo_agent_odoo.py` - CFO agent tests
3. `test_admin_agent_odoo.py` - Admin agent tests
4. `test_agent_graph_v3_odoo.py` - Agent graph tests
5. `test_rbac_integration.py` - RBAC tests
6. `test_agent_integration.py` - End-to-end tests

---

## Expected Outcomes

After completing Task 1.5, we should have:

1. **Verified Functionality**
   - All agents work with OdooClient
   - Agent graph executes correctly
   - RBAC enforces permissions
   - Error handling is robust

2. **Test Coverage**
   - Individual agent tests: 90%+
   - Agent graph tests: 80%+
   - RBAC tests: 100%
   - Integration tests: 70%+

3. **Documentation**
   - Test report with results
   - Known issues documented
   - Performance metrics
   - Recommendations for improvements

4. **Readiness for Task 1.6**
   - Agents are stable
   - Dashboard can integrate safely
   - API endpoints are reliable
   - System is production-ready

---

## Next Steps After Task 1.5

**Task 1.6: Dashboard Integration (1 day)**
- Connect dashboard to agent graph
- Display real-time agent status
- Show conversation history
- Enable agent controls
- Test dashboard functionality

**Module 1 Completion**
- All tasks complete
- System ready for PIM module
- Production deployment possible
- First client ready

---

## Notes

- Focus on OdooClient integration
- Verify RBAC works correctly
- Test error scenarios
- Document edge cases
- Prepare for dashboard integration
