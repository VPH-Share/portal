# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        try:
            # Deleting model 'scsWorkflow'
            db.delete_table('scs_workflows_scsworkflow')
        except Exception, e:
            pass

        # Adding model 'Resource'
        db.create_table('scs_resources_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('global_id', self.gf('django.db.models.fields.CharField')(max_length=39, null=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['auth.User'])),
            ('security_policy', self.gf('django.db.models.fields.CharField')(max_length=125, null=True, blank=True)),
            ('security_configuration', self.gf('django.db.models.fields.CharField')(max_length=125, null=True, blank=True)),
        ))
        db.send_create_signal('scs_resources', ['Resource'])

        # Adding model 'ResourceRequest'
        db.create_table('scs_resources_resourcerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scs_resources.Resource'])),
            ('requestor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('scs_resources', ['ResourceRequest'])

        # Adding model 'Workflow'
        db.create_table('scs_resources_workflow', (
            ('resource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['scs_resources.Resource'], unique=True, primary_key=True)),
            ('t2flow', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('xml', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('scs_resources', ['Workflow'])


    def backwards(self, orm):
        # Deleting model 'Resource'
        db.delete_table('scs_resources_resource')

        # Deleting model 'ResourceRequest'
        db.delete_table('scs_resources_resourcerequest')

        # Deleting model 'Workflow'
        db.delete_table('scs_resources_workflow')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'scs_resources.resource': {
            'Meta': {'object_name': 'Resource'},
            'global_id': ('django.db.models.fields.CharField', [], {'max_length': '39', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['auth.User']"}),
            'security_configuration': ('django.db.models.fields.CharField', [], {'max_length': '125', 'null': 'True', 'blank': 'True'}),
            'security_policy': ('django.db.models.fields.CharField', [], {'max_length': '125', 'null': 'True', 'blank': 'True'})
        },
        'scs_resources.resourcerequest': {
            'Meta': {'object_name': 'ResourceRequest'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'requestor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scs_resources.Resource']"})
        },
        'scs_resources.workflow': {
            'Meta': {'object_name': 'Workflow', '_ormbases': ['scs_resources.Resource']},
            'resource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['scs_resources.Resource']", 'unique': 'True', 'primary_key': 'True'}),
            't2flow': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'xml': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['scs_resources']