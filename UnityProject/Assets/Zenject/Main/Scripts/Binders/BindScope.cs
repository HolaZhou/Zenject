﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ModestTree;

namespace Zenject
{
    // This class is meant to be used the following way:
    //
    //  using (var scope = _container.CreateScope())
    //  {
    //      scope.Bind(playerWrapper);
    //      ...
    //      ...
    //      var bar = _container.Resolve<Foo>();
    //  }
    public class BindScope : IDisposable
    {
        DiContainer _container;
        List<ProviderBase> _scopedProviders = new List<ProviderBase>();
        SingletonProviderMap _singletonMap;
        PrefabSingletonProviderMap _prefabSingletonMap;

        internal BindScope(DiContainer container, SingletonProviderMap singletonMap, PrefabSingletonProviderMap prefabSingletonMap)
        {
            _container = container;
            _singletonMap = singletonMap;
            _prefabSingletonMap = prefabSingletonMap;
        }

        public BinderUntyped Bind(Type contractType)
        {
            return Bind(contractType, null);
        }

        public BinderUntyped Bind(Type contractType, string identifier)
        {
            return new CustomScopeUntypedBinder(this, contractType, identifier, _container, _singletonMap, _prefabSingletonMap);
        }

        public ReferenceBinder<TContract> Bind<TContract>() where TContract : class
        {
            return Bind<TContract>((string)null);
        }

        public ReferenceBinder<TContract> Bind<TContract>(string identifier) where TContract : class
        {
            return new CustomScopeReferenceBinder<TContract>(this, identifier, _container, _singletonMap, _prefabSingletonMap);
        }

        public ValueBinder<TContract> BindValue<TContract>() where TContract : struct
        {
            return BindValue<TContract>((string)null);
        }

        public ValueBinder<TContract> BindValue<TContract>(string identifier) where TContract : struct
        {
            return new CustomScopeValueBinder<TContract>(this, identifier, _container);
        }

        // This method is just an alternative way of binding to a dependency of
        // a specific class with a specific identifier
        public void BindIdentifier<TClass, TParam>(string identifier, TParam value)
            where TParam : class
        {
            Bind(typeof(TParam), identifier).To(value).WhenInjectedInto<TClass>();

            // We'd pref to do this instead but it fails on web player because Mono
            // seems to interpret TDerived : TBase to require that TDerived != TBase?
            //Bind<TParam>().To(value).WhenInjectedInto<TClass>().As(identifier);
        }

        void AddProvider(ProviderBase provider)
        {
            Assert.That(!_scopedProviders.Contains(provider));
            _scopedProviders.Add(provider);
        }

        public void Dispose()
        {
            foreach (var provider in _scopedProviders)
            {
                _container.UnregisterProvider(provider);
            }
        }

        class CustomScopeValueBinder<TContract> : ValueBinder<TContract> where TContract : struct
        {
            BindScope _owner;

            public CustomScopeValueBinder(
                BindScope owner, string identifier,
                DiContainer container)
                : base(container, identifier)
            {
                _owner = owner;
            }

            public override BindingConditionSetter ToProvider(ProviderBase provider)
            {
                _owner.AddProvider(provider);
                return base.ToProvider(provider);
            }
        }

        class CustomScopeReferenceBinder<TContract> : ReferenceBinder<TContract> where TContract : class
        {
            BindScope _owner;

            public CustomScopeReferenceBinder(
                BindScope owner, string identifier,
                DiContainer container, SingletonProviderMap singletonMap, PrefabSingletonProviderMap prefabSingletonMap)
                : base(container, identifier, singletonMap, prefabSingletonMap)
            {
                _owner = owner;
            }

            public override BindingConditionSetter ToProvider(ProviderBase provider)
            {
                _owner.AddProvider(provider);
                return base.ToProvider(provider);
            }
        }

        class CustomScopeUntypedBinder : BinderUntyped
        {
            BindScope _owner;

            public CustomScopeUntypedBinder(
                BindScope owner, Type contractType, string identifier,
                DiContainer container, SingletonProviderMap singletonMap, PrefabSingletonProviderMap prefabSingletonMap)
                : base(container, contractType, identifier, singletonMap, prefabSingletonMap)
            {
                _owner = owner;
            }

            public override BindingConditionSetter ToProvider(ProviderBase provider)
            {
                _owner.AddProvider(provider);
                return base.ToProvider(provider);
            }
        }
    }
}
