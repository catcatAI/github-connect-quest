import React, { useCallback, useState } from 'react';
import {
  ReactFlow,
  addEdge,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Connection,
  Edge,
  Node,
  NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Settings, Save, Download, Upload } from 'lucide-react';

// 模組類型定義
interface ModuleData extends Record<string, unknown> {
  id: string;
  label: string;
  type: 'model' | 'tool' | 'core-ai' | 'service' | 'data-store' | 'interface';
  status: 'completed' | 'built-in' | 'downloadable' | 'in-progress';
  description: string;
  location?: string;
}

// 自定義節點組件
const ModuleNode: React.FC<{ data: ModuleData }> = ({ data }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'built-in': return 'bg-blue-500';
      case 'downloadable': return 'bg-orange-500';
      case 'in-progress': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'model': return '🤖';
      case 'tool': return '🔧';
      case 'core-ai': return '🧠';
      case 'service': return '⚙️';
      case 'data-store': return '💾';
      case 'interface': return '🖥️';
      default: return '📦';
    }
  };

  return (
    <Card className="min-w-[200px] shadow-lg">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{getTypeIcon(data.type)}</span>
          <CardTitle className="text-sm">{data.label}</CardTitle>
          <Badge className={`${getStatusColor(data.status)} text-white text-xs`}>
            {data.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">{data.description}</p>
        {data.location && (
          <p className="text-xs text-blue-600 mt-1">{data.location}</p>
        )}
      </CardContent>
    </Card>
  );
};

// 初始節點數據
const initialNodes: Node[] = [
  // Models
  {
    id: 'math-model',
    type: 'module',
    position: { x: 100, y: 100 },
    data: {
      id: 'math-model',
      label: 'Math Model',
      type: 'model',
      status: 'built-in',
      description: 'Lightweight model for basic arithmetic problems',
      location: 'src/tools/math_model/'
    }
  },
  {
    id: 'logic-model',
    type: 'module',
    position: { x: 300, y: 100 },
    data: {
      id: 'logic-model',
      label: 'Logic Model',
      type: 'model',
      status: 'built-in',
      description: 'Lightweight model for basic logic problems',
      location: 'src/tools/logic_model/'
    }
  },
  {
    id: 'image-recognition-model',
    type: 'module',
    position: { x: 500, y: 100 },
    data: {
      id: 'image-recognition-model',
      label: 'Image Recognition Model',
      type: 'model',
      status: 'downloadable',
      description: 'Image recognition using template matching',
      location: 'src/tools/image_recognition_tool.py'
    }
  },
  // Tools
  {
    id: 'math-tool',
    type: 'module',
    position: { x: 100, y: 300 },
    data: {
      id: 'math-tool',
      label: 'Math Tool',
      type: 'tool',
      status: 'completed',
      description: 'Tool for basic arithmetic problems',
      location: 'src/tools/math_tool.py'
    }
  },
  {
    id: 'calculator-tool',
    type: 'module',
    position: { x: 300, y: 300 },
    data: {
      id: 'calculator-tool',
      label: 'Calculator Tool',
      type: 'tool',
      status: 'completed',
      description: 'Calculate mathematical expressions',
      location: 'src/tools/calculator_tool.py'
    }
  },
  // Core AI
  {
    id: 'dialogue-manager',
    type: 'module',
    position: { x: 100, y: 500 },
    data: {
      id: 'dialogue-manager',
      label: 'Dialogue Manager',
      type: 'core-ai',
      status: 'completed',
      description: 'Manages AI conversations and responses'
    }
  },
  {
    id: 'learning-manager',
    type: 'module',
    position: { x: 300, y: 500 },
    data: {
      id: 'learning-manager',
      label: 'Learning Manager',
      type: 'core-ai',
      status: 'completed',
      description: 'Handles learning and adaptation'
    }
  },
  {
    id: 'ham-memory',
    type: 'module',
    position: { x: 500, y: 500 },
    data: {
      id: 'ham-memory',
      label: 'HAM Memory Manager',
      type: 'core-ai',
      status: 'completed',
      description: 'Hierarchical memory management system'
    }
  },
  {
    id: 'tool-dispatcher',
    type: 'module',
    position: { x: 700, y: 500 },
    data: {
      id: 'tool-dispatcher',
      label: 'Tool Dispatcher',
      type: 'core-ai',
      status: 'completed',
      description: 'Routes and executes tool requests'
    }
  },
  // Services
  {
    id: 'main-api-server',
    type: 'module',
    position: { x: 100, y: 700 },
    data: {
      id: 'main-api-server',
      label: 'Main API Server',
      type: 'service',
      status: 'completed',
      description: 'FastAPI backend server'
    }
  },
  {
    id: 'llm-interface',
    type: 'module',
    position: { x: 300, y: 700 },
    data: {
      id: 'llm-interface',
      label: 'LLM Interface',
      type: 'service',
      status: 'completed',
      description: 'Interface to language models'
    }
  },
  // Interfaces
  {
    id: 'cli-interface',
    type: 'module',
    position: { x: 100, y: 900 },
    data: {
      id: 'cli-interface',
      label: 'CLI Interface',
      type: 'interface',
      status: 'completed',
      description: 'Command line interface'
    }
  },
  {
    id: 'electron-app',
    type: 'module',
    position: { x: 300, y: 900 },
    data: {
      id: 'electron-app',
      label: 'Electron App',
      type: 'interface',
      status: 'completed',
      description: 'Desktop application interface'
    }
  }
];

// 初始連接線
const initialEdges: Edge[] = [
  // Tools connect to models
  { id: 'e1', source: 'math-tool', target: 'math-model', type: 'smoothstep' },
  { id: 'e2', source: 'calculator-tool', target: 'math-model', type: 'smoothstep' },
  
  // Core AI connections
  { id: 'e3', source: 'dialogue-manager', target: 'learning-manager', type: 'smoothstep' },
  { id: 'e4', source: 'dialogue-manager', target: 'ham-memory', type: 'smoothstep' },
  { id: 'e5', source: 'dialogue-manager', target: 'tool-dispatcher', type: 'smoothstep' },
  { id: 'e6', source: 'tool-dispatcher', target: 'math-tool', type: 'smoothstep' },
  { id: 'e7', source: 'tool-dispatcher', target: 'calculator-tool', type: 'smoothstep' },
  
  // Services connect to core AI
  { id: 'e8', source: 'main-api-server', target: 'dialogue-manager', type: 'smoothstep' },
  { id: 'e9', source: 'llm-interface', target: 'dialogue-manager', type: 'smoothstep' },
  
  // Interfaces connect to services
  { id: 'e10', source: 'cli-interface', target: 'main-api-server', type: 'smoothstep' },
  { id: 'e11', source: 'electron-app', target: 'main-api-server', type: 'smoothstep' }
];

const nodeTypes: NodeTypes = {
  module: ModuleNode,
};

export default function ArchitectureEditor() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [editingNode, setEditingNode] = useState<ModuleData | null>(null);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const addNewModule = () => {
    const newNode: Node = {
      id: `module-${Date.now()}`,
      type: 'module',
      position: { x: Math.random() * 500, y: Math.random() * 500 },
      data: {
        id: `module-${Date.now()}`,
        label: 'New Module',
        type: 'tool',
        status: 'in-progress',
        description: 'New module description'
      }
    };
    setNodes((nds) => [...nds, newNode]);
    setIsAddDialogOpen(false);
  };

  const editModule = (moduleData: ModuleData) => {
    setEditingNode(moduleData);
  };

  const saveModule = (updatedData: ModuleData) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === updatedData.id
          ? { ...node, data: updatedData }
          : node
      )
    );
    setEditingNode(null);
  };

  return (
    <div className="h-full w-full flex flex-col">
      {/* 工具欄 */}
      <div className="flex items-center gap-2 p-4 border-b bg-background">
        <Button onClick={() => setIsAddDialogOpen(true)} size="sm">
          <Plus className="w-4 h-4 mr-2" />
          添加模組
        </Button>
        <Button variant="outline" size="sm">
          <Save className="w-4 h-4 mr-2" />
          保存
        </Button>
        <Button variant="outline" size="sm">
          <Download className="w-4 h-4 mr-2" />
          導出
        </Button>
        <Button variant="outline" size="sm">
          <Upload className="w-4 h-4 mr-2" />
          導入
        </Button>
      </div>

      {/* React Flow 編輯器 */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          onNodeDoubleClick={(_, node) => editModule(node.data as ModuleData)}
        >
          <Controls />
          <MiniMap />
          <Background />
        </ReactFlow>
      </div>

      {/* 添加模組對話框 */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>添加新模組</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">名稱</Label>
              <Input id="name" placeholder="模組名稱" className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="type" className="text-right">類型</Label>
              <Select>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="選擇模組類型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="model">模型</SelectItem>
                  <SelectItem value="tool">工具</SelectItem>
                  <SelectItem value="core-ai">核心AI</SelectItem>
                  <SelectItem value="service">服務</SelectItem>
                  <SelectItem value="data-store">數據存儲</SelectItem>
                  <SelectItem value="interface">介面</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">描述</Label>
              <Textarea id="description" placeholder="模組描述" className="col-span-3" />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={addNewModule}>添加</Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* 編輯模組對話框 */}
      {editingNode && (
        <Dialog open={!!editingNode} onOpenChange={() => setEditingNode(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>編輯模組: {editingNode.label}</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-name" className="text-right">名稱</Label>
                <Input 
                  id="edit-name" 
                  value={editingNode.label} 
                  onChange={(e) => setEditingNode({...editingNode, label: e.target.value})}
                  className="col-span-3" 
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-type" className="text-right">類型</Label>
                <Select value={editingNode.type} onValueChange={(value) => setEditingNode({...editingNode, type: value as any})}>
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="model">模型</SelectItem>
                    <SelectItem value="tool">工具</SelectItem>
                    <SelectItem value="core-ai">核心AI</SelectItem>
                    <SelectItem value="service">服務</SelectItem>
                    <SelectItem value="data-store">數據存儲</SelectItem>
                    <SelectItem value="interface">介面</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-status" className="text-right">狀態</Label>
                <Select value={editingNode.status} onValueChange={(value) => setEditingNode({...editingNode, status: value as any})}>
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="completed">已完成</SelectItem>
                    <SelectItem value="built-in">內建</SelectItem>
                    <SelectItem value="downloadable">可下載</SelectItem>
                    <SelectItem value="in-progress">進行中</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-description" className="text-right">描述</Label>
                <Textarea 
                  id="edit-description" 
                  value={editingNode.description} 
                  onChange={(e) => setEditingNode({...editingNode, description: e.target.value})}
                  className="col-span-3" 
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-location" className="text-right">位置</Label>
                <Input 
                  id="edit-location" 
                  value={editingNode.location || ''} 
                  onChange={(e) => setEditingNode({...editingNode, location: e.target.value})}
                  className="col-span-3" 
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setEditingNode(null)}>
                取消
              </Button>
              <Button onClick={() => saveModule(editingNode)}>保存</Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}