// Atlassian API 接口定义
import { useState, useEffect } from 'react';

export interface AtlassianConfig {
  domain: string;
  userEmail: string;
  apiToken: string;
  cloudId: string;
}

export interface AtlassianService {
  name: string;
  status: 'connected' | 'disconnected' | 'error';
  lastSync: string;
  health: number;
}

export interface ConfluenceSpace {
  id: string;
  key: string;
  name: string;
  type: string;
  status: string;
}

export interface ConfluencePage {
  id: string;
  title: string;
  type: string;
  status: string;
  space: {
    key: string;
    name: string;
  };
  version: {
    number: number;
  };
  _links: {
    webui: string;
  };
}

export interface JiraProject {
  id: string;
  key: string;
  name: string;
  projectTypeKey: string;
  simplified: boolean;
  style: string;
}

export interface JiraIssue {
  id: string;
  key: string;
  fields: {
    summary: string;
    description?: any;
    status: {
      name: string;
      statusCategory: {
        name: string;
      };
    };
    issuetype: {
      name: string;
      iconUrl: string;
    };
    priority: {
      name: string;
      iconUrl: string;
    };
    assignee?: {
      displayName: string;
      emailAddress: string;
    };
    created: string;
    updated: string;
  };
}

export interface RovoDevTask {
  taskId: string;
  capability: string;
  parameters: Record<string, any>;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  error?: string;
  createdAt: string;
  completedAt?: string;
}

export interface RovoDevAgent {
  agentId: string;
  isActive: boolean;
  capabilities: string[];
  queueSize: number;
  activeTasks: number;
  metrics: {
    tasksCompleted: number;
    tasksFailed: number;
    averageResponseTime: number;
    lastActivity: string;
  };
}

// API 客户端类
export class AtlassianApiClient {
  private baseUrl: string;
  private config: AtlassianConfig;

  constructor(config: AtlassianConfig) {
    this.config = config;
    this.baseUrl = 'http://localhost:8000/api'; // 假设后端 API 地址
  }

  // 配置管理
  async testConnection(): Promise<{ [service: string]: boolean }> {
    const response = await fetch(`${this.baseUrl}/atlassian/test-connection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(this.config),
    });
    return response.json();
  }

  async saveConfig(config: AtlassianConfig): Promise<boolean> {
    const response = await fetch(`${this.baseUrl}/atlassian/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return response.ok;
  }

  // Confluence API
  async getConfluenceSpaces(): Promise<ConfluenceSpace[]> {
    const response = await fetch(`${this.baseUrl}/atlassian/confluence/spaces`, {
      headers: this.getAuthHeaders(),
    });
    return response.json();
  }

  async getConfluencePages(spaceKey: string): Promise<ConfluencePage[]> {
    const response = await fetch(
      `${this.baseUrl}/atlassian/confluence/spaces/${spaceKey}/pages`,
      {
        headers: this.getAuthHeaders(),
      }
    );
    return response.json();
  }

  async createConfluencePage(
    spaceKey: string,
    title: string,
    content: string,
    parentId?: string
  ): Promise<ConfluencePage> {
    const response = await fetch(`${this.baseUrl}/atlassian/confluence/pages`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        spaceKey,
        title,
        content,
        parentId,
      }),
    });
    return response.json();
  }

  // Jira API
  async getJiraProjects(): Promise<JiraProject[]> {
    const response = await fetch(`${this.baseUrl}/atlassian/jira/projects`, {
      headers: this.getAuthHeaders(),
    });
    return response.json();
  }

  async getJiraIssues(projectKey: string): Promise<JiraIssue[]> {
    const response = await fetch(
      `${this.baseUrl}/atlassian/jira/projects/${projectKey}/issues`,
      {
        headers: this.getAuthHeaders(),
      }
    );
    return response.json();
  }

  async createJiraIssue(
    projectKey: string,
    summary: string,
    description: string,
    issueType: string = 'Task',
    priority: string = 'Medium'
  ): Promise<JiraIssue> {
    const response = await fetch(`${this.baseUrl}/atlassian/jira/issues`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        projectKey,
        summary,
        description,
        issueType,
        priority,
      }),
    });
    return response.json();
  }

  async searchJiraIssues(jql: string): Promise<JiraIssue[]> {
    const response = await fetch(`${this.baseUrl}/atlassian/jira/search`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ jql }),
    });
    const data = await response.json();
    return data.issues || [];
  }

  // Rovo Dev Agent API
  async getRovoDevAgentStatus(): Promise<RovoDevAgent> {
    const response = await fetch(`${this.baseUrl}/rovo-dev/status`, {
      headers: this.getAuthHeaders(),
    });
    return response.json();
  }

  async submitRovoDevTask(
    capability: string,
    parameters: Record<string, any>
  ): Promise<RovoDevTask> {
    const response = await fetch(`${this.baseUrl}/rovo-dev/tasks`, {
      method: 'POST',
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        capability,
        parameters,
      }),
    });
    return response.json();
  }

  async getRovoDevTasks(): Promise<RovoDevTask[]> {
    const response = await fetch(`${this.baseUrl}/rovo-dev/tasks`, {
      headers: this.getAuthHeaders(),
    });
    return response.json();
  }

  async getRovoDevTaskHistory(limit: number = 50): Promise<RovoDevTask[]> {
    const response = await fetch(
      `${this.baseUrl}/rovo-dev/tasks/history?limit=${limit}`,
      {
        headers: this.getAuthHeaders(),
      }
    );
    return response.json();
  }

  // 辅助方法
  private getAuthHeaders(): Record<string, string> {
    return {
      'X-Atlassian-Domain': this.config.domain,
      'X-Atlassian-Email': this.config.userEmail,
      'X-Atlassian-Token': this.config.apiToken,
      'X-Atlassian-Cloud-ID': this.config.cloudId,
    };
  }
}

// React Hook for Atlassian API
export function useAtlassianApi(config?: AtlassianConfig) {
  const [client, setClient] = useState<AtlassianApiClient | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [services, setServices] = useState<AtlassianService[]>([]);

  useEffect(() => {
    if (config) {
      const apiClient = new AtlassianApiClient(config);
      setClient(apiClient);
      
      // 测试连接
      apiClient.testConnection().then((results) => {
        setIsConnected(Object.values(results).some(Boolean));
        setServices([
          {
            name: 'Confluence',
            status: results.confluence ? 'connected' : 'disconnected',
            lastSync: new Date().toISOString(),
            health: results.confluence ? 100 : 0,
          },
          {
            name: 'Jira',
            status: results.jira ? 'connected' : 'disconnected',
            lastSync: new Date().toISOString(),
            health: results.jira ? 100 : 0,
          },
        ]);
      }).catch(() => {
        setIsConnected(false);
        setServices([
          {
            name: 'Confluence',
            status: 'error',
            lastSync: new Date().toISOString(),
            health: 0,
          },
          {
            name: 'Jira',
            status: 'error',
            lastSync: new Date().toISOString(),
            health: 0,
          },
        ]);
      });
    }
  }, [config]);

  return {
    client,
    isConnected,
    services,
  };
}